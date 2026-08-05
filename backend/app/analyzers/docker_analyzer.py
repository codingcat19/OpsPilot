from app.parsers.base import Finding


class DockerAnalyzer:
    """Docker-specific analysis rules."""

    async def analyze(self, parsed_data: dict) -> list[Finding]:
        # TODO: implement Dockerfile-specific rules
        raise NotImplementedError
