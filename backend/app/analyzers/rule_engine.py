from app.analyzers.docker_analyzer import DockerAnalyzer
from app.analyzers.terraform_analyzer import TerraformAnalyzer
from app.parsers.base import Finding


class RuleEngine:
    """Rule-based analysis engine. Dispatches parsed content to the matching analyzer."""

    _analyzer_classes: dict[str, type] = {
        "docker": DockerAnalyzer,
        "terraform": TerraformAnalyzer,
    }

    async def evaluate(self, parsed_data: dict, file_type: str) -> list[Finding]:
        analyzer_class = self._analyzer_classes.get(file_type)
        if analyzer_class is None:
            return []  # no rule-based findings for unimplemented types
        return await analyzer_class().analyze(parsed_data)
