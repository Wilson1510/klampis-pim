from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.services.user_service import user_service
from app.schemas.user_schema import (
    UserResponse,
    UserCreate,
    UserUpdate
)
from app.schemas.base import SingleItemResponse, MultipleItemsResponse
from app.utils.response_helpers import (
    create_single_item_response,
    create_multiple_items_response
)
from app.api.v1.dependencies.auth import get_current_user
from app.models import Users

router = APIRouter()


@router.get(
    "/",
    response_model=MultipleItemsResponse[UserResponse],
    status_code=status.HTTP_200_OK
)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    username: Optional[str] = Query(
        None, description="Filter by username (partial match)"
    ),
    email: Optional[str] = Query(
        None, description="Filter by email (partial match)"
    ),
    name: Optional[str] = Query(
        None, description="Filter by name (partial match)"
    ),
    role: Optional[str] = Query(
        None, description="Filter by role (ADMIN, MANAGER, SYSTEM, USER)"
    ),
    is_active: Optional[bool] = Query(
        None, description="Filter by active status"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get users with optional filtering and pagination.

    **Requires ADMIN role** (enforced at router level).

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **username**: Filter by username (partial match)
    - **email**: Filter by email (partial match)
    - **name**: Filter by name (partial match)
    - **role**: Filter by role (ADMIN, MANAGER, SYSTEM, USER)
    - **is_active**: Filter by active status (true/false)
    """
    users, total = await user_service.get_users_with_filter(
        db=db,
        skip=skip,
        limit=limit,
        username=username,
        email=email,
        name=name,
        role=role,
        is_active=is_active
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=users,
        page=page,
        limit=limit,
        total=total
    )


@router.post(
    "/",
    response_model=SingleItemResponse[UserResponse],
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)  # Need user ID for created_by
):
    """
    Create a new user.

    **Requires ADMIN role** (enforced at router level).

    Creates a new user with the provided information.
    Username and email must be unique across the system.
    """
    user = await user_service.create_user(
        db=db,
        user_create=user_create,
        created_by=current_user.id
    )
    return create_single_item_response(data=user)


@router.get(
    "/{user_id}",
    response_model=SingleItemResponse[UserResponse],
    status_code=status.HTTP_200_OK
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID.

    **Requires ADMIN role** (enforced at router level).

    Returns detailed information about a specific user.
    """
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    return create_single_item_response(data=user)


@router.put(
    "/{user_id}",
    response_model=SingleItemResponse[UserResponse],
    status_code=status.HTTP_200_OK
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)  # Need user ID for updated_by
):
    """
    Update user by ID.

    **Requires ADMIN role** (enforced at router level).

    Updates user information. Only provided fields will be updated.
    Username and email must remain unique if changed.
    """
    user = await user_service.update_user(
        db=db,
        user_id=user_id,
        user_update=user_update,
        updated_by=current_user.id
    )
    return create_single_item_response(data=user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user by ID.

    **Requires ADMIN role** (enforced at router level).

    System and Admin users cannot be deleted.
    """
    await user_service.delete_user(db, user_id=user_id)
