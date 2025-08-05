from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Users
from app.schemas.user_schema import UserCreate, UserUpdate
from app.repositories.base import CRUDBase


class UserRepository(CRUDBase[Users, UserCreate, UserUpdate]):
    """Repository for user operations."""

    async def get_multi_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        username: Optional[str] = None,
        email: Optional[str] = None,
        name: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Users]:
        """Get users with filtering and pagination."""
        query = select(self.model)

        conditions = []

        if username is not None:
            conditions.append(self.model.username == username)

        if email is not None:
            conditions.append(self.model.email.ilike(f"%{email}%"))

        if name is not None:
            conditions.append(self.model.name.ilike(f"%{name}%"))

        if role is not None:
            conditions.append(self.model.role == role)

        if is_active is not None:
            conditions.append(self.model.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_next_sequence(self, db: AsyncSession) -> int:
        """Get next sequence number for user."""
        query = select(func.coalesce(func.max(self.model.sequence), 0) + 1)
        result = await db.execute(query)
        return result.scalar()

    async def create(self, db: AsyncSession, obj_in: Users) -> Users:
        """Create user with model instance."""
        db.add(obj_in)
        await db.commit()
        await db.refresh(obj_in)
        return obj_in

    async def update(self, db: AsyncSession, db_obj: Users, update_data: dict) -> Users:
        """Update user with dict data."""
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


user_repository = UserRepository(Users)
