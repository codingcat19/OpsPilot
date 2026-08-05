from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ProjectRepository(db)

    async def list_projects(self, owner_id: str) -> list[dict]:
        # TODO: implement
        raise NotImplementedError

    async def create_project(self, name: str, description: str | None, owner_id: str) -> dict:
        # TODO: implement
        raise NotImplementedError
