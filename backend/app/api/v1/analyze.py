from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzers.engine import AnalyzerEngine
from app.database import get_db

router = APIRouter()


@router.post("/docker")
async def analyze_dockerfile(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
) -> dict:
    # TODO: implement Dockerfile analysis
    raise NotImplementedError


@router.post("/terraform")
async def analyze_terraform(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
) -> dict:
    content = await file.read()
    try:
        findings = await AnalyzerEngine().analyze(content, "terraform")
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Failed to parse Terraform file: {exc}"
        ) from exc
    return {"file_type": "terraform", "findings": [finding.model_dump() for finding in findings]}


@router.post("/github-actions")
async def analyze_github_actions(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
) -> dict:
    # TODO: implement GitHub Actions analysis
    raise NotImplementedError


@router.post("/logs")
async def analyze_logs(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> dict:
    # TODO: implement log analysis
    raise NotImplementedError
