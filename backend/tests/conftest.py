import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.database import engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
async def clean_database():
    async with engine.begin() as conn:
        tables = "users, projects, analyses, findings, reports"
        await conn.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
