from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis, Finding, Report
from app.parsers.base import Finding as FindingData


class AnalysisService:
    """Orchestrates the full analysis pipeline: parse -> rules -> AI -> persist."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def run_analysis(
        self, project_id: str, file_type: str, file_name: str, content: bytes
    ) -> Analysis:
        # TODO: implement full pipeline
        # 1. Create Analysis record (status=pending)
        # 2. Parse file
        # 3. Run rule engine
        # 4. Persist findings
        # 5. Call AI provider for explanations
        # 6. Create Report
        # 7. Update status to completed
        raise NotImplementedError
