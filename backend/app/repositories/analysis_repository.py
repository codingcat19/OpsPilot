import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis


class AnalysisRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, analysis_id: uuid.UUID) -> Analysis | None:
        result = await self.db.execute(select(Analysis).where(Analysis.id == analysis_id))
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: uuid.UUID) -> Sequence[Analysis]:
        result = await self.db.execute(
            select(Analysis).where(Analysis.project_id == project_id)
        )
        return result.scalars().all()

    async def create(self, analysis: Analysis) -> Analysis:
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis
