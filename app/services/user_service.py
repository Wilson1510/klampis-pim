from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models import Users
from app.repositories import user_repository
from app.schemas.user_schema import UserCreate, UserUpdate, UserChangePassword
from app.core.security import verify_password
from app.core.config import settings


class UserService:
    """Service for user business logic."""

    def __init__(self):
        self.repository = user_repository

    async def authenticate_user(
        self, db: AsyncSession, username: str, password: str
    ) -> Optional[Users]:
        """
        Authenticate user with username and password.

        Args:
            db: Database session
            username: Username
            password: Plain password

        Returns:
            Optional[Users]: User if authentication successful, None otherwise
        """
        user = await self.repository.get_by_field(db, 'username', username)
        if (
            not user
            or not user.is_active
            or not verify_password(password, user.password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await db.commit()

        return user

    async def get_all_users(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Users], int]:
        """Get all users with pagination and total count."""
        data = await self.repository.get_multi(db, skip=skip, limit=limit)
        total = len(data)
        return data, total

    async def create_user(
        self, db: AsyncSession, user_create: UserCreate, created_by: int
    ) -> Users:
        """
        Create a new user.

        Args:
            db: Database session
            user_create: User creation data
            created_by: ID of user creating this user

        Returns:
            Users: Created user

        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username exists
        existing_username = await self.repository.get_by_field(
            db, 'username', user_create.username
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with username '{user_create.username}' already exists"
            )

        # Check if email exists
        existing_email = await self.repository.get_by_field(
            db, 'email', user_create.email
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{user_create.email}' already exists"
            )

        # Get next sequence number
        next_sequence = await self.repository.get_next_sequence(db)

        # Create user
        user_data = user_create.model_dump()
        # Password will be hashed automatically by the listener
        user_data["created_by"] = created_by
        user_data["updated_by"] = created_by
        user_data["sequence"] = next_sequence

        user = Users(**user_data)
        return await self.repository.create(db, obj_in=user)

    async def get_users_with_filter(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        username: Optional[str] = None,
        email: Optional[str] = None,
        name: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Users], int]:
        """Get users with filtering."""
        if (
            username is None and email is None and name is None
            and role is None and is_active is None
        ):
            return await self.get_all_users(db, skip=skip, limit=limit)

        data = await self.repository.get_multi_with_filter(
            db=db,
            skip=skip,
            limit=limit,
            username=username,
            email=email,
            name=name,
            role=role,
            is_active=is_active
        )
        total = len(data)
        return data, total

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[Users]:
        """Get user by ID."""
        return await self.repository.get(db, user_id)

    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        user_update: UserUpdate,
        updated_by: int
    ) -> Users:
        """
        Update user.

        Args:
            db: Database session
            user_id: User ID to update
            user_update: User update data
            updated_by: ID of user making the update

        Returns:
            Users: Updated user

        Raises:
            HTTPException: If user not found or validation fails
        """
        user = await self.repository.get(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        # Check username uniqueness if being updated
        if user_update.username and user_update.username != user.username:
            existing_username = await self.repository.get_by_field(
                db, 'username', user_update.username
            )
            if existing_username and existing_username.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with username '{user_update.username}' already exists"
                )

        # Check email uniqueness if being updated
        if user_update.email and user_update.email != user.email:
            existing_email = await self.repository.get_by_field(
                db, 'email', user_update.email
            )
            if existing_email and existing_email.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email '{user_update.email}' already exists"
                )

        # Update user
        update_data = user_update.model_dump(exclude_unset=True)
        update_data["updated_by"] = updated_by

        return await self.repository.update(db, user, update_data)

    async def delete_user(self, db: AsyncSession, user_id: int) -> Users:
        """
        Args:
            db: Database session
            user_id: User ID to delete

        Returns:
            Users: Deleted user

        Raises:
            HTTPException: If user not found or is system/admin user
        """
        user = await self.repository.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        # Prevent deletion of system and admin users
        if user.id in [settings.SYSTEM_USER_ID, settings.ADMIN_USER_ID]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete system or admin user"
            )

        return await self.repository.delete(db, id=user_id)

    async def change_password(
        self,
        db: AsyncSession,
        user_id: int,
        password_change: UserChangePassword
    ) -> Users:
        """
        Change user password.

        Args:
            db: Database session
            user_id: User ID
            password_change: Password change data

        Returns:
            Users: Updated user

        Raises:
            HTTPException: If user not found or current password is incorrect
        """
        user = await self.repository.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        # Verify current password
        if not verify_password(password_change.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        update_data = {
            "password": password_change.new_password,
            "updated_by": user_id
        }

        return await self.repository.update(db, user, update_data)


user_service = UserService()
