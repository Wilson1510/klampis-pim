from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.services.user_service import user_service
from app.schemas.user_schema import (
    UserResponse,
    UserUpdate,
    UserChangePassword
)
from app.schemas.base import SingleItemResponse
from app.utils.response_helpers import create_single_item_response
from app.api.v1.dependencies.auth import get_current_user
from app.models import Users

router = APIRouter()


@router.get(
    "/me",
    response_model=SingleItemResponse[UserResponse],
    status_code=status.HTTP_200_OK
)
async def get_my_profile(
    current_user: Users = Depends(get_current_user)
):
    """
    Get current user's profile.

    **Requires authentication** (enforced at router level).
    All authenticated users can view their own profile.
    """
    return create_single_item_response(data=current_user)


@router.put(
    "/me",
    response_model=SingleItemResponse[UserResponse],
    status_code=status.HTTP_200_OK
)
async def update_my_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Update current user's profile.

    **Requires authentication** (enforced at router level).
    Users can update their own profile information.

    **Restrictions:**
    - Users cannot change their own role
    - Users cannot change their active status
    """
    # Prevent users from changing their own role or active status
    if user_update.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change your own role"
        )

    if user_update.is_active is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change your own active status"
        )

    user = await user_service.update_user(
        db=db,
        user_id=current_user.id,
        user_update=user_update,
        updated_by=current_user.id
    )
    return create_single_item_response(data=user)


@router.post(
    "/change-password",
    response_model=SingleItemResponse[UserResponse],
    status_code=status.HTTP_200_OK
)
async def change_my_password(
    password_change: UserChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Change current user's password.

    **Requires authentication** (enforced at router level).
    All authenticated users can change their own password.

    **Validation Rules:**
    - Current password must be correct
    - New password must be at least 6 characters long
    - New password must be different from current password
    """
    user = await user_service.change_password(
        db=db,
        user_id=current_user.id,
        password_change=password_change
    )
    return create_single_item_response(data=user)
