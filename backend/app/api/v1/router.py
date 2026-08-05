from fastapi import APIRouter

from app.api.v1 import auth, projects, analyze, reports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])


@api_router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
