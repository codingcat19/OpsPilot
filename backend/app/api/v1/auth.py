from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.auth.schemas import Token, UserCreate, UserLogin, UserResponse
from app.auth.service import AuthService
from app.database import get_db
from app.models.analysis import User

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = AuthService(db)
    user = await service.register(email=body.email, password=body.password)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and receive an access token",
)
async def login(
    body: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    service = AuthService(db)
    user = await service.authenticate(email=body.email, password=body.password)
    token = AuthService.create_access_token(str(user.id))
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)
