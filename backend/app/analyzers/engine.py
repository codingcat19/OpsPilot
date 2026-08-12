from app.analyzers.rule_engine import RuleEngine
from app.parsers.base import BaseParser, Finding
from app.parsers.docker_parser import DockerParser


class AnalyzerEngine:
    """Orchestrates the analysis pipeline: parse -> rules -> findings."""

    _parser_classes: dict[str, type[BaseParser]] = {
        "docker": DockerParser,
    }

    def __init__(self, rule_engine: RuleEngine | None = None) -> None:
        self.rule_engine = rule_engine or RuleEngine()

    async def analyze(self, content: bytes, file_type: str) -> list[Finding]:
        parser_class = self._parser_classes.get(file_type)
        if parser_class is None:
            raise ValueError(f"Unsupported file type: {file_type}")
        parsed_data = await parser_class().parse(content)
        return await self.rule_engine.evaluate(parsed_data, file_type)
