from app.parsers.base import Finding

_SOURCE = "terraform"

_PUBLIC_ACLS = {"public-read", "public-read-write", "website"}
_OPEN_CIDR = {"0.0.0.0/0", "::/0"}
_SECRET_KEY_RE = ("password", "passwd", "secret", "token", "api_key", "access_key", "secret_key")
_TAGGABLE = {
    "aws_s3_bucket",
    "aws_instance",
    "aws_db_instance",
    "aws_security_group",
    "aws_ebs_volume",
}
_SECRET_ATTRS = ("password", "secret", "access_key", "secret_key", "token")


def _is_truthy(value: object) -> bool:
    return value is True or value == "true"


def _is_literal(value: object) -> bool:
    return isinstance(value, str) and "${" not in value


class TerraformAnalyzer:
    """Terraform-specific analysis rules."""

    async def analyze(self, parsed_data: dict) -> list[Finding]:
        resources = parsed_data.get("resources", [])
        variables = parsed_data.get("variables", [])
        checks = (
            self._check_public_s3,
            self._check_open_security_group,
            self._check_unencrypted_ebs,
            self._check_unencrypted_rds,
            self._check_unencrypted_s3,
            self._check_public_rds,
            self._check_secret_variable,
            self._check_hardcoded_credentials,
            self._check_missing_tags,
            self._check_default_vpc,
        )
        findings: list[Finding] = []
        for check in checks:
            findings.extend(check(resources, variables))
        return findings

    @staticmethod
    def _check_public_s3(resources: list[dict], variables: list[dict]) -> list[Finding]:
        findings: list[Finding] = []
        for resource in resources:
            attrs = resource["attrs"]
            if resource["type"] == "aws_s3_bucket_public_access_block":
                if not _is_truthy(attrs.get("block_public_acls", False)) or not _is_truthy(
                    attrs.get("block_public_policy", False)
                ):
                    findings.append(
                        Finding(
                            title="Public access not blocked on S3 bucket",
                            severity="high",
                            description=f"aws_s3_bucket_public_access_block {resource['name']!r} "
                            "does not block public ACLs and policies.",
                            recommendation="Set block_public_acls and block_public_policy to true.",
                            source=_SOURCE,
                        )
                    )
                continue
            if resource["type"] != "aws_s3_bucket":
                continue
            acl = attrs.get("acl")
            if _is_literal(acl) and acl in _PUBLIC_ACLS:
                findings.append(
                    Finding(
                        title="S3 bucket has public ACL",
                        severity="critical",
                        description=f"aws_s3_bucket {resource['name']!r} uses ACL {acl!r}.",
                        recommendation=(
                            "Use private ACL and a public_access_block to lock the bucket down."
                        ),
                        source=_SOURCE,
                    )
                )
        return findings

    @staticmethod
    def _check_open_security_group(resources: list[dict], variables: list[dict]) -> list[Finding]:
        findings: list[Finding] = []
        for resource in resources:
            if resource["type"] not in ("aws_security_group", "aws_security_group_rule"):
                continue
            rules = resource["attrs"].get("ingress", resource["attrs"].get("egress"))
            if isinstance(rules, dict):
                rules = [rules]
            if not isinstance(rules, list):
                continue
            for rule in rules:
                if isinstance(rule, str):
                    continue
                cidrs = rule.get("cidr_blocks", [])
                if isinstance(cidrs, str):
                    cidrs = [cidrs]
                if any(_is_literal(cidr) and cidr in _OPEN_CIDR for cidr in cidrs):
                    findings.append(
                        Finding(
                            title="Security group open to the world",
                            severity="critical",
                            description=f"{resource['type']} {resource['name']!r} allows traffic "
                            f"from {_OPEN_CIDR}.",
                            recommendation="Restrict cidr_blocks to specific private networks.",
                            source=_SOURCE,
                        )
                    )
                    break
        return findings

    @staticmethod
    def _check_unencrypted_ebs(resources: list[dict], variables: list[dict]) -> list[Finding]:
        for resource in resources:
            if resource["type"] == "aws_ebs_volume" and not _is_truthy(
                resource["attrs"].get("encrypted", False)
            ):
                return [
                    Finding(
                        title="EBS volume not encrypted",
                        severity="high",
                        description=f"aws_ebs_volume {resource['name']!r} has encryption disabled.",
                        recommendation="Set encrypted = true on the volume.",
                        source=_SOURCE,
                    )
                ]
        return []

    @staticmethod
    def _check_unencrypted_rds(resources: list[dict], variables: list[dict]) -> list[Finding]:
        for resource in resources:
            if resource["type"] == "aws_db_instance" and not _is_truthy(
                resource["attrs"].get("storage_encrypted", False)
            ):
                return [
                    Finding(
                        title="RDS instance not encrypted",
                        severity="high",
                        description=f"aws_db_instance {resource['name']!r} has "
                        "unencrypted storage.",
                        recommendation="Set storage_encrypted = true.",
                        source=_SOURCE,
                    )
                ]
        return []

    @staticmethod
    def _check_unencrypted_s3(resources: list[dict], variables: list[dict]) -> list[Finding]:
        for resource in resources:
            if resource[
                "type"
            ] == "aws_s3_bucket" and "server_side_encryption_configuration" not in (
                resource["attrs"] or {}
            ):
                return [
                    Finding(
                        title="S3 bucket not encrypted",
                        severity="high",
                        description=f"aws_s3_bucket {resource['name']!r} has no "
                        "server-side encryption.",
                        recommendation=(
                            "Add server_side_encryption_configuration with SSE-S3 or KMS."
                        ),
                        source=_SOURCE,
                    )
                ]
        return []

    @staticmethod
    def _check_public_rds(resources: list[dict], variables: list[dict]) -> list[Finding]:
        for resource in resources:
            if resource["type"] == "aws_db_instance" and _is_truthy(
                resource["attrs"].get("publicly_accessible", False)
            ):
                return [
                    Finding(
                        title="RDS instance publicly accessible",
                        severity="high",
                        description=f"aws_db_instance {resource['name']!r} is "
                        "exposed to the internet.",
                        recommendation=(
                            "Set publicly_accessible = false and use a private subnet."
                        ),
                        source=_SOURCE,
                    )
                ]
        return []

    @staticmethod
    def _check_secret_variable(resources: list[dict], variables: list[dict]) -> list[Finding]:
        findings: list[Finding] = []
        for variable in variables:
            default = variable["attrs"].get("default")
            if not _is_literal(default):
                continue
            if any(key in variable["name"].lower() for key in _SECRET_KEY_RE) or any(
                key in str(default).lower() for key in _SECRET_KEY_RE
            ):
                findings.append(
                    Finding(
                        title="Secret value in variable default",
                        severity="critical",
                        description=f"variable {variable['name']!r} has a literal "
                        "default that looks like a secret.",
                        recommendation="Use an environment variable or secrets manager reference.",
                        source=_SOURCE,
                    )
                )
        return findings

    @staticmethod
    def _check_hardcoded_credentials(resources: list[dict], variables: list[dict]) -> list[Finding]:
        for resource in resources:
            for key, value in resource["attrs"].items():
                if any(attr in key.lower() for attr in _SECRET_ATTRS) and _is_literal(value):
                    return [
                        Finding(
                            title="Hard-coded credential in resource",
                            severity="critical",
                            description=f"{resource['type']} {resource['name']!r} sets "
                            f"{key!r} to a literal value.",
                            recommendation="Reference a variable or secrets manager instead.",
                            source=_SOURCE,
                        )
                    ]
        return []

    @staticmethod
    def _check_missing_tags(resources: list[dict], variables: list[dict]) -> list[Finding]:
        findings: list[Finding] = []
        for resource in resources:
            if resource["type"] not in _TAGGABLE:
                continue
            tags = resource["attrs"].get("tags")
            if not isinstance(tags, dict) or not tags:
                findings.append(
                    Finding(
                        title="Resource missing tags",
                        severity="low",
                        description=f"{resource['type']} {resource['name']!r} has no tags.",
                        recommendation="Add a tags block with owner, environment, and project.",
                        source=_SOURCE,
                    )
                )
        return findings

    @staticmethod
    def _check_default_vpc(resources: list[dict], variables: list[dict]) -> list[Finding]:
        for resource in resources:
            if resource["type"] == "aws_default_vpc":
                return [
                    Finding(
                        title="Default VPC in use",
                        severity="medium",
                        description="The Terraform configuration adopts the default VPC.",
                        recommendation=(
                            "Provision a dedicated VPC with proper subnet and routing design."
                        ),
                        source=_SOURCE,
                    )
                ]
        return []
