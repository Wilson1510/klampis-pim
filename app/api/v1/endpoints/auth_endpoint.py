from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)
from app.services.user_service import user_service
from app.schemas.user_schema import UserLogin, Token, TokenRefresh, UserProfile
from app.api.v1.dependencies.auth import get_current_user
from app.models import Users

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    User login endpoint.

    Authenticates user with username and password, returns JWT tokens.

    - **username**: User's username
    - **password**: User's password

    Returns access token and refresh token for authenticated requests.
    """
    user = await user_service.authenticate_user(
        db, user_login.username, user_login.password
    )

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    token_data = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

    return token_data


@router.post(
    "/refresh",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def refresh_token(
    token_refresh: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid refresh token

    Returns new access token and refresh token.
    """
    user_id = verify_refresh_token(token_refresh.refresh_token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    user = await user_service.get_user_by_id(db, user_id_int)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)

    token_data = Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )

    return token_data


@router.get(
    "/me",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK
)
async def get_current_user_profile(
    current_user: Users = Depends(get_current_user)
):
    """
    Get current user profile.

    Returns the profile information of the currently authenticated user.
    Requires valid JWT token in Authorization header.
    """
    user_profile = UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        is_active=current_user.is_active,
        last_login=current_user.last_login
    )

    return user_profile


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
async def logout(
    current_user: Users = Depends(get_current_user)
):
    """
    User logout endpoint.

    Note: Since we're using stateless JWT tokens, this endpoint
    doesn't actually invalidate the token server-side.
    The client should discard the token.

    In a production environment, you might want to implement
    a token blacklist or use shorter token expiration times.
    """
    return {
        "success": True,
        "message": "Successfully logged out",
        "detail": "Please discard your access token"
    }
