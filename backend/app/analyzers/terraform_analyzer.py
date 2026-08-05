from app.parsers.base import Finding


class TerraformAnalyzer:
    """Terraform-specific analysis rules."""

    async def analyze(self, parsed_data: dict) -> list[Finding]:
        # TODO: implement Terraform-specific rules
        raise NotImplementedError
