from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.post("/login")
async def login(db: AsyncSession = Depends(get_db)) -> dict:
    # TODO: implement JWT login
    raise NotImplementedError


@router.post("/register")
async def register(db: AsyncSession = Depends(get_db)) -> dict:
    # TODO: implement user registration
    raise NotImplementedError
