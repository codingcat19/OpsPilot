from app.analyzers.rule_engine import RuleEngine
from app.parsers.base import Finding


class AnalyzerEngine:
    """Orchestrates the analysis pipeline: parse -> rules -> findings."""

    def __init__(self, rule_engine: RuleEngine) -> None:
        self.rule_engine = rule_engine

    async def analyze(self, content: bytes, file_type: str) -> list[Finding]:
        # TODO: implement pipeline orchestration
        # 1. Select parser by file_type
        # 2. Parse content
        # 3. Run rule engine
        # 4. Return findings
        raise NotImplementedError
