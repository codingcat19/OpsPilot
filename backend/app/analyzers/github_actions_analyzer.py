from app.parsers.base import Finding


class GitHubActionsAnalyzer:
    """GitHub Actions-specific analysis rules."""

    async def analyze(self, parsed_data: dict) -> list[Finding]:
        # TODO: implement GitHub Actions-specific rules
        raise NotImplementedError
