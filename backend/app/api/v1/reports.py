from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/{report_id}")
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    # TODO: implement get report
    raise NotImplementedError
