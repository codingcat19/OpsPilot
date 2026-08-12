import pytest

from app.analyzers.docker_analyzer import DockerAnalyzer
from app.analyzers.engine import AnalyzerEngine
from app.analyzers.rule_engine import RuleEngine
from app.parsers.docker_parser import DockerParser


async def parse(dockerfile: str) -> dict:
    return await DockerParser().parse(dockerfile.encode())


async def analyze(dockerfile: str) -> list:
    parsed = await DockerParser().parse(dockerfile.encode())
    return await DockerAnalyzer().analyze(parsed)


async def finding_titles(dockerfile: str) -> set[str]:
    return {f.title for f in await analyze(dockerfile)}


# --- Parser ---


async def test_parse_plain_dockerfile():
    dockerfile = """
FROM python:3.12-slim
WORKDIR /app
COPY . .
CMD ["python", "app.py"]
"""
    data = await parse(dockerfile)
    assert data["file_type"] == "docker"
    assert [i["instruction"] for i in data["instructions"]] == ["FROM", "WORKDIR", "COPY", "CMD"]
    assert data["stages"] == [{"image": "python", "tag": "3.12-slim", "alias": None}]


async def test_parse_multistage_with_continuations_and_comments():
    dockerfile = """
# syntax=docker/dockerfile:1
FROM python:3.12 AS builder
RUN pip install \\
    requests \\
    flask
FROM python:3.12-slim
COPY --from=builder /app /app
"""
    data = await parse(dockerfile)
    assert [i["instruction"] for i in data["instructions"]] == ["FROM", "RUN", "FROM", "COPY"]
    assert data["instructions"][1]["value"] == "pip install requests flask"
    assert data["stages"][0]["alias"] == "builder"
    assert data["stages"][1]["alias"] is None


async def test_parse_is_case_insensitive():
    data = await parse("from busybox as build\nexpose 8080\n")
    assert data["instructions"][0]["instruction"] == "FROM"
    assert data["stages"][0] == {"image": "busybox", "tag": None, "alias": "build"}
    assert data["instructions"][1]["instruction"] == "EXPOSE"


async def test_parse_digest_and_registry_port_not_tag():
    digest = await parse("FROM alpine@sha256:abc123\n")
    assert digest["stages"][0]["tag"] == "@sha256:abc123"
    registry = await parse("FROM registry:5000/app\n")
    assert registry["stages"][0]["image"] == "registry:5000/app"
    assert registry["stages"][0]["tag"] is None


async def test_parse_empty_content():
    data = await parse("")
    assert data["instructions"] == []
    assert data["stages"] == []


# --- Analyzer rules ---


async def test_missing_user_flag_is_high():
    assert "Missing USER instruction" in await finding_titles("FROM python:3.12\nRUN echo hi\n")


async def test_user_present_suppresses_root_finding():
    titles = await finding_titles("FROM python:3.12\nUSER 10001\nRUN echo hi\n")
    assert "Missing USER instruction" not in titles


async def test_latest_base_image_flagged():
    assert "Base image tag not pinned" in await finding_titles("FROM python:latest\n")


async def test_no_tag_base_image_flagged():
    assert "Base image tag not pinned" in await finding_titles("FROM python\n")


async def test_pinned_base_image_not_flagged():
    titles = await finding_titles("FROM python:3.12-slim\n")
    assert "Base image tag not pinned" not in titles


async def test_add_over_copy_flagged_but_url_and_archive_ok():
    assert "ADD used instead of COPY" in await finding_titles(
        "FROM python:3.12\nADD app.py /app/\n"
    )
    urls = "FROM python:3.12\nADD https://example.com/file /app/\nADD bundle.tar.gz /app/\n"
    assert "ADD used instead of COPY" not in await finding_titles(urls)


async def test_secret_in_env_is_critical():
    dockerfile = "FROM python:3.12\nENV API_KEY=abcdef1234\n"
    findings = await analyze(dockerfile)
    secrets = [f for f in findings if f.title == "Secret value in ENV/ARG"]
    assert secrets and secrets[0].severity == "critical"


async def test_secret_reference_not_flagged():
    dockerfile = "FROM python:3.12\nENV API_KEY=${API_KEY}\nARG DB_PASSWORD=$DB_PASSWORD\n"
    assert "Secret value in ENV/ARG" not in await finding_titles(dockerfile)


async def test_pipe_to_shell_flagged():
    dockerfile = "FROM python:3.12\nRUN curl -fsSL https://x.sh | sh\n"
    assert "Remote script piped to shell" in await finding_titles(dockerfile)


async def test_apt_cleanup_flagged():
    dockerfile = "FROM python:3.12\nRUN apt-get update && apt-get install -y curl\n"
    assert "apt lists not cleaned up" in await finding_titles(dockerfile)


async def test_apt_cleanup_not_flagged_when_removed():
    dockerfile = (
        "FROM python:3.12\nRUN apt-get update && apt-get install -y curl "
        "&& rm -rf /var/lib/apt/lists/*\n"
    )
    assert "apt lists not cleaned up" not in await finding_titles(dockerfile)


async def test_pip_cache_flagged():
    dockerfile = "FROM python:3.12\nRUN pip install requests\n"
    assert "pip cache left in image" in await finding_titles(dockerfile)


async def test_pip_no_cache_dir_not_flagged():
    dockerfile = "FROM python:3.12\nRUN pip install --no-cache-dir requests\n"
    assert "pip cache left in image" not in await finding_titles(dockerfile)


async def test_missing_healthcheck_is_info():
    findings = await analyze("FROM python:3.12\nEXPOSE 8080\n")
    healthchecks = [f for f in findings if f.title == "Missing HEALTHCHECK"]
    assert healthchecks and healthchecks[0].severity == "info"


async def test_ssh_port_exposed_is_low():
    dockerfile = "FROM ubuntu:24.04\nRUN apt-get update && apt-get install -y ssh\nEXPOSE 22\n"
    findings = await analyze(dockerfile)
    ssh = [f for f in findings if f.title == "SSH port exposed"]
    assert ssh and ssh[0].severity == "low"


async def test_well_configured_dockerfile_has_no_non_info_findings():
    dockerfile = """\
FROM python:3.12-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir requests
USER 10001
HEALTHCHECK CMD curl -f http://localhost:8080/ || exit 1
EXPOSE 8080
"""
    findings = await analyze(dockerfile)
    assert findings == []


# --- RuleEngine + AnalyzerEngine ---


async def test_rule_engine_unknown_type_returns_empty():
    findings = await RuleEngine().evaluate({"instructions": []}, "unknown")
    assert findings == []


async def test_rule_engine_dispatches_docker():
    parsed = await DockerParser().parse(b"FROM python\n")
    titles = {f.title for f in await RuleEngine().evaluate(parsed, "docker")}
    assert "Base image tag not pinned" in titles


async def test_engine_end_to_end_docker():
    dockerfile = b"FROM python\nRUN pip install requests\n"
    findings = await AnalyzerEngine().analyze(dockerfile, "docker")
    titles = {f.title for f in findings}
    assert "Base image tag not pinned" in titles
    assert "pip cache left in image" in titles
    assert all(f.source == "docker" for f in findings)


async def test_engine_unsupported_file_type_raises():
    with pytest.raises(ValueError, match="Unsupported file type"):
        await AnalyzerEngine().analyze(b"{}", "yaml")
