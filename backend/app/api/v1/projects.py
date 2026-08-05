from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_projects(db: AsyncSession = Depends(get_db)) -> list[dict]:
    # TODO: implement list projects
    raise NotImplementedError


@router.post("/")
async def create_project(db: AsyncSession = Depends(get_db)) -> dict:
    # TODO: implement create project
    raise NotImplementedError
