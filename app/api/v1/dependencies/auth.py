from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.core.security import verify_token
from app.models import Users, Role
from app.repositories.user_repository import user_repository

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Users:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        Users: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    user_id = verify_token(token)

    if user_id is None:
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise credentials_exception

    user = await user_repository.get(db, id=user_id_int)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_admin_user(
    current_user: Users = Depends(get_current_user)
) -> Users:
    """
    Get current user and ensure they have ADMIN role.
    Used for admin-only endpoints.
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_manager_or_admin_user(
    current_user: Users = Depends(get_current_user)
) -> Users:
    """
    Get current user and ensure they have ADMIN, MANAGER, or SYSTEM role.
    Used for management-level endpoints.
    """
    if current_user.role not in [Role.ADMIN, Role.MANAGER, Role.SYSTEM]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Admin access required"
        )
    return current_user


def check_resource_ownership(current_user: Users, resource_created_by: int) -> bool:
    """
    Check if user can modify a resource based on ownership and role.

    Rules:
    - ADMIN: Can modify any resource
    - MANAGER, SYSTEM: Can modify any resource
    - USER: Can only modify their own resources

    Args:
        current_user: Current authenticated user
        resource_created_by: ID of user who created the resource

    Returns:
        bool: True if user can modify the resource
    """
    # ADMIN, MANAGER, SYSTEM can modify any resource
    if current_user.role in [Role.ADMIN, Role.MANAGER, Role.SYSTEM]:
        return True

    # USER can only modify their own resources
    return current_user.id == resource_created_by


def require_resource_ownership(current_user: Users, resource_created_by: int):
    """
    Raise exception if user doesn't have permission to modify resource.

    Args:
        current_user: Current authenticated user
        resource_created_by: ID of user who created the resource

    Raises:
        HTTPException: If user doesn't have permission
    """
    if not check_resource_ownership(current_user, resource_created_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own resources"
        )
