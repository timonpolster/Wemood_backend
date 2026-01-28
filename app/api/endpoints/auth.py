from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse, UserInfo
from app.core.jwt import create_access_token
from app.core.security import get_current_user
from app.core.logging_config import get_logger

logger = get_logger("api.auth")

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Admin Login",
    description="Authenticate with username and password to receive a JWT access token."
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    user_repo = UserRepository(db)
    user = await user_repo.authenticate(form_data.username, form_data.password)
    
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.username)
    logger.info(f"Successful login for user: {user.username}")
    
    return TokenResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=UserInfo,
    summary="Get Current User",
    description="Get information about the currently authenticated user."
)
async def get_me(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserInfo:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(current_user)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserInfo(username=user.username, is_active=user.is_active)
