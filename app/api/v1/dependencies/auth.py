from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.core.security import verify_token
from app.models.user_model import Users, Role
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

    user = await user_repository.get_by_id(db, user_id_int)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


# Role-based access control dependencies
async def require_admin(
    current_user: Users = Depends(get_current_user)
) -> Users:
    """Require ADMIN role."""
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_admin_or_manager(
    current_user: Users = Depends(get_current_user)
) -> Users:
    """Require ADMIN or MANAGER role."""
    if current_user.role not in [Role.ADMIN, Role.MANAGER, Role.SYSTEM]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin, Manager, or System access required"
        )
    return current_user


def check_ownership_or_admin(current_user: Users, resource_created_by: int) -> bool:
    """
    Check if user owns the resource or is admin/manager/system.

    Args:
        current_user: Current authenticated user
        resource_created_by: ID of user who created the resource

    Returns:
        bool: True if user can access the resource
    """
    # Admin, Manager, and System can access all resources
    if current_user.role in [Role.ADMIN, Role.MANAGER, Role.SYSTEM]:
        return True

    # User can only access their own resources
    return current_user.id == resource_created_by


async def can_modify_resource(
    resource_created_by: int,
    current_user: Users = Depends(get_current_user)
) -> Users:
    """
    Check if user can modify resources (not just USER role or owns the resource).
    This dependency should be used with additional ownership checks in the endpoint.
    """
    if (
        current_user.role in [Role.ADMIN, Role.MANAGER, Role.SYSTEM]
        or current_user.id == resource_created_by
    ):
        return current_user
