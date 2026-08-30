import pytest
from lark.exceptions import UnexpectedInput

from app.analyzers.engine import AnalyzerEngine
from app.analyzers.rule_engine import RuleEngine
from app.analyzers.terraform_analyzer import TerraformAnalyzer
from app.parsers.terraform_parser import TerraformParser


async def parse(terraform: str) -> dict:
    return await TerraformParser().parse(terraform.encode())


async def analyze(terraform: str) -> list:
    parsed = await TerraformParser().parse(terraform.encode())
    return await TerraformAnalyzer().analyze(parsed)


async def finding_titles(terraform: str) -> set[str]:
    return {f.title for f in await analyze(terraform)}


# --- Parser ---


async def test_parse_plain_terraform():
    terraform = """
resource "aws_s3_bucket" "b" {
  bucket = "my-bucket"
  acl    = "private"
}
"""
    data = await parse(terraform)
    assert data["file_type"] == "terraform"
    assert data["resources"][0]["type"] == "aws_s3_bucket"
    assert data["resources"][0]["name"] == "b"
    assert data["resources"][0]["attrs"] == {"bucket": "my-bucket", "acl": "private"}


async def test_parse_nested_and_typed_values():
    terraform = """
resource "aws_security_group" "sg" {
  name   = "web"
  ingress {
    from_port   = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8", "0.0.0.0/0"]
  }
}
"""
    data = await parse(terraform)
    sg = data["resources"][0]
    assert sg["attrs"]["ingress"][0]["from_port"] == 22
    assert sg["attrs"]["ingress"][0]["cidr_blocks"] == ["10.0.0.0/8", "0.0.0.0/0"]
    assert "__is_block__" not in sg["attrs"]["ingress"][0]


async def test_parse_variables():
    terraform = """
variable "region" {
  type    = string
  default = "us-east-1"
}
variable "db_password" {
  default = "hunter2"
}
"""
    data = await parse(terraform)
    assert [v["name"] for v in data["variables"]] == ["region", "db_password"]
    assert data["variables"][1]["attrs"]["default"] == "hunter2"


async def test_parse_expressions_not_quoted():
    terraform = """
variable "env" {
  default = "dev"
}
resource "aws_s3_bucket" "b" {
  bucket = "${var.env}-bucket"
  acl    = var.acl
}
"""
    data = await parse(terraform)
    attrs = data["resources"][0]["attrs"]
    assert attrs["bucket"] == "${var.env}-bucket"
    assert attrs["acl"] == "${var.acl}"


async def test_parse_empty_content():
    data = await parse("")
    assert data["resources"] == []
    assert data["variables"] == []


async def test_parse_invalid_hcl_raises():
    with pytest.raises(UnexpectedInput):
        await TerraformParser().parse(b"resource aws_s3_bucket { bucket =")


# --- Analyzer rules ---


async def test_public_s3_acl_critical():
    terraform = 'resource "aws_s3_bucket" "b" {\n  acl = "public-read"\n}\n'
    findings = await analyze(terraform)
    assert "S3 bucket has public ACL" in {f.title for f in findings}
    assert any(f.severity == "critical" for f in findings)


async def test_private_s3_acl_not_flagged():
    terraform = 'resource "aws_s3_bucket" "b" {\n  acl = "private"\n}\n'
    assert "S3 bucket has public ACL" not in await finding_titles(terraform)


async def test_public_access_block_missing_blocked():
    terraform = """
resource "aws_s3_bucket" "b" {
  acl = "private"
}
resource "aws_s3_bucket_public_access_block" "b" {
  bucket = aws_s3_bucket.b.id
}
"""
    assert "Public access not blocked on S3 bucket" in await finding_titles(terraform)


async def test_open_security_group_critical():
    terraform = """
resource "aws_security_group" "sg" {
  name = "web"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
"""
    findings = await analyze(terraform)
    open_sg = [f for f in findings if f.title == "Security group open to the world"]
    assert open_sg and open_sg[0].severity == "critical"


async def test_restricted_security_group_not_flagged():
    terraform = """
resource "aws_security_group" "sg" {
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}
"""
    assert "Security group open to the world" not in await finding_titles(terraform)


async def test_unencrypted_ebs_flagged():
    terraform = 'resource "aws_ebs_volume" "vol" {\n  size = 10\n  encrypted = false\n}\n'
    assert "EBS volume not encrypted" in await finding_titles(terraform)


async def test_encrypted_ebs_not_flagged():
    terraform = 'resource "aws_ebs_volume" "vol" {\n  encrypted = true\n}\n'
    assert "EBS volume not encrypted" not in await finding_titles(terraform)


async def test_unencrypted_rds_flagged():
    terraform = 'resource "aws_db_instance" "db" {\n  storage_encrypted = false\n}\n'
    assert "RDS instance not encrypted" in await finding_titles(terraform)


async def test_unencrypted_s3_flagged():
    terraform = 'resource "aws_s3_bucket" "b" {\n  acl = "private"\n}\n'
    assert "S3 bucket not encrypted" in await finding_titles(terraform)


async def test_encrypted_s3_not_flagged():
    terraform = """
resource "aws_s3_bucket" "b" {
  acl = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "aws:kms"
      }
    }
  }
}
"""
    assert "S3 bucket not encrypted" not in await finding_titles(terraform)


async def test_public_rds_flagged():
    terraform = 'resource "aws_db_instance" "db" {\n  publicly_accessible = true\n}\n'
    assert "RDS instance publicly accessible" in await finding_titles(terraform)


async def test_secret_variable_default_critical():
    terraform = 'variable "db_password" {\n  default = "hunter2"\n}\n'
    findings = await analyze(terraform)
    secrets = [f for f in findings if f.title == "Secret value in variable default"]
    assert secrets and secrets[0].severity == "critical"


async def test_non_secret_variable_not_flagged():
    terraform = 'variable "region" {\n  default = "us-east-1"\n}\n'
    assert "Secret value in variable default" not in await finding_titles(terraform)


async def test_hardcoded_credential_flagged():
    terraform = """
resource "aws_instance" "web" {
  ami           = "ami-123"
  instance_type = "t2.micro"
  access_key    = "AKIA1234567890"
}
"""
    assert "Hard-coded credential in resource" in await finding_titles(terraform)


async def test_missing_tags_flagged():
    terraform = """
resource "aws_instance" "web" {
  ami           = "ami-123"
  instance_type = "t2.micro"
}
"""
    assert "Resource missing tags" in await finding_titles(terraform)


async def test_tagged_resource_not_flagged():
    terraform = """
resource "aws_instance" "web" {
  ami           = "ami-123"
  instance_type = "t2.micro"
  tags = {
    Name        = "web"
    Environment = "prod"
  }
}
"""
    assert "Resource missing tags" not in await finding_titles(terraform)


async def test_default_vpc_flagged():
    terraform = 'resource "aws_default_vpc" "default" {}\n'
    assert "Default VPC in use" in await finding_titles(terraform)


async def test_well_configured_terraform():
    terraform = """
resource "aws_s3_bucket" "b" {
  bucket = "my-bucket"
  acl    = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "aws:kms"
      }
    }
  }
  tags = {
    Name = "b"
  }
}
resource "aws_security_group" "sg" {
  name = "private"
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
  tags = {
    Name = "sg"
  }
}
"""
    assert await analyze(terraform) == []


# --- RuleEngine + AnalyzerEngine ---


async def test_rule_engine_dispatches_terraform():
    parsed = await TerraformParser().parse(
        b'resource "aws_s3_bucket" "b" {\n acl = "public-read"\n}'
    )
    titles = {f.title for f in await RuleEngine().evaluate(parsed, "terraform")}
    assert "S3 bucket has public ACL" in titles


async def test_engine_end_to_end_terraform():
    content = b'resource "aws_s3_bucket" "b" {\n acl = "public-read"\n}'
    findings = await AnalyzerEngine().analyze(content, "terraform")
    titles = {f.title for f in findings}
    assert "S3 bucket has public ACL" in titles
    assert all(f.source == "terraform" for f in findings)


async def test_engine_terraform_now_supported():
    findings = await AnalyzerEngine().analyze(b'resource "aws_s3_bucket" "b" {}', "terraform")
    assert isinstance(findings, list)
