from app.parsers.base import Finding


class RuleEngine:
    """Rule-based analysis engine. Evaluates parsed content against defined rules."""

    async def evaluate(self, parsed_data: dict, file_type: str) -> list[Finding]:
        # TODO: implement rule evaluation
        # Rule-based analysis first, AI explanations second
        raise NotImplementedError
