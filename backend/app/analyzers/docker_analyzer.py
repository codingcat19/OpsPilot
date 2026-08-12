import re

from app.parsers.base import Finding

_SOURCE = "docker"

_SECRET_KEYS = re.compile(
    r"(PASSWORD|PASSWD|SECRET|TOKEN|API_?KEY|ACCESS_?KEY|PRIVATE_?KEY|CREDENTIAL)", re.I
)
_PIPE_TO_SHELL = re.compile(r"\|\s*(ba)?sh\b")
_APT_INSTALL = re.compile(r"apt-get\s+(install|update)\b")
_APT_CLEANUP = re.compile(r"rm\s+-rf\s+.*/var/lib/apt/lists")
_PIP_INSTALL = re.compile(r"\b(python\s+-m\s+pip|pip3?)\s+install\b")
_URL_RE = re.compile(r"^https?://")
_ARCHIVE_RE = re.compile(r"\.(tar(\.(gz|bz2|xz))?|tgz|zip)$", re.I)


class DockerAnalyzer:
    """Docker-specific analysis rules."""

    async def analyze(self, parsed_data: dict) -> list[Finding]:
        instructions = parsed_data.get("instructions", [])
        stages = parsed_data.get("stages", [])
        checks = (
            self._check_root_user,
            self._check_unpinned_base_image,
            self._check_add_over_copy,
            self._check_secret_in_env,
            self._check_pipe_to_shell,
            self._check_apt_cleanup,
            self._check_pip_cache,
            self._check_missing_healthcheck,
            self._check_ssh_exposed,
        )
        return [finding for check in checks if (finding := check(instructions, stages)) is not None]

    @staticmethod
    def _check_root_user(instructions: list[dict], stages: list[dict]) -> Finding | None:
        if any(i["instruction"] == "USER" for i in instructions):
            return None
        return Finding(
            title="Missing USER instruction",
            severity="high",
            description="The Dockerfile never switches away from the default root user.",
            recommendation="Add a non-root USER directive (e.g. USER 10001) before COPY/RUN.",
            source=_SOURCE,
        )

    @staticmethod
    def _check_unpinned_base_image(instructions: list[dict], stages: list[dict]) -> Finding | None:
        if not stages:
            return None
        tag = stages[-1]["tag"]
        if tag is not None and tag.lower() != "latest":
            return None
        return Finding(
            title="Base image tag not pinned",
            severity="medium",
            description=f"Final stage uses base image tag {tag or '(none)'}, which can drift.",
            recommendation="Pin the base image to an explicit checkable tag or digest.",
            source=_SOURCE,
        )

    @staticmethod
    def _check_add_over_copy(instructions: list[dict], stages: list[dict]) -> Finding | None:
        for i in instructions:
            if i["instruction"] != "ADD":
                continue
            source = i["value"].split()[0]
            if _URL_RE.match(source) or _ARCHIVE_RE.search(source):
                continue
            return Finding(
                title="ADD used instead of COPY",
                severity="medium",
                description=f"ADD on line {i['line']} copies local files; COPY suffices.",
                recommendation="Use COPY for local files; ADD is for URLs or archive extraction.",
                source=_SOURCE,
            )
        return None

    @staticmethod
    def _check_secret_in_env(instructions: list[dict], stages: list[dict]) -> Finding | None:
        for i in instructions:
            if i["instruction"] not in ("ENV", "ARG"):
                continue
            key, sep, value = i["value"].partition("=")
            key = key.strip()
            if not sep or not _SECRET_KEYS.search(key):
                continue
            value = value.strip().strip('"')
            if value and not value.startswith("$"):
                return Finding(
                    title="Secret value in ENV/ARG",
                    severity="critical",
                    description=f"{i['instruction']} on line {i['line']} hardcodes {key!r}.",
                    recommendation="Use build args or runtime secrets instead of literal values.",
                    source=_SOURCE,
                )
        return None

    @staticmethod
    def _check_pipe_to_shell(instructions: list[dict], stages: list[dict]) -> Finding | None:
        for i in instructions:
            if i["instruction"] == "RUN" and _PIPE_TO_SHELL.search(i["value"]):
                return Finding(
                    title="Remote script piped to shell",
                    severity="high",
                    description=f"RUN on line {i['line']} pipes a downloaded script into a shell.",
                    recommendation="Download the script first, review it, then execute it.",
                    source=_SOURCE,
                )
        return None

    @staticmethod
    def _check_apt_cleanup(instructions: list[dict], stages: list[dict]) -> Finding | None:
        for i in instructions:
            apt = _APT_INSTALL.search(i["value"])
            if i["instruction"] == "RUN" and apt and not _APT_CLEANUP.search(i["value"]):
                return Finding(
                    title="apt lists not cleaned up",
                    severity="medium",
                    description=f"RUN on line {i['line']} runs apt-get without cleaning the index.",
                    recommendation="Add '&& rm -rf /var/lib/apt/lists/*' to the same RUN.",
                    source=_SOURCE,
                )
        return None

    @staticmethod
    def _check_pip_cache(instructions: list[dict], stages: list[dict]) -> Finding | None:
        for i in instructions:
            pinned = "--no-cache-dir" in i["value"]
            if i["instruction"] == "RUN" and _PIP_INSTALL.search(i["value"]) and not pinned:
                return Finding(
                    title="pip cache left in image",
                    severity="medium",
                    description=f"RUN on line {i['line']} runs pip without --no-cache-dir.",
                    recommendation="Install with 'pip install --no-cache-dir'.",
                    source=_SOURCE,
                )
        return None

    @staticmethod
    def _check_missing_healthcheck(instructions: list[dict], stages: list[dict]) -> Finding | None:
        if any(i["instruction"] == "HEALTHCHECK" for i in instructions):
            return None
        return Finding(
            title="Missing HEALTHCHECK",
            severity="info",
            description="No HEALTHCHECK is declared, so failure detection is left to the host.",
            recommendation="Add a HEALTHCHECK CMD appropriate for the service.",
            source=_SOURCE,
        )

    @staticmethod
    def _check_ssh_exposed(instructions: list[dict], stages: list[dict]) -> Finding | None:
        for i in instructions:
            if i["instruction"] == "EXPOSE" and "22" in re.findall(r"\d+", i["value"]):
                return Finding(
                    title="SSH port exposed",
                    severity="low",
                    description=f"EXPOSE on line {i['line']} publishes SSH port 22.",
                    recommendation="Do not expose port 22 unless the image is a bastion/jump host.",
                    source=_SOURCE,
                )
        return None
