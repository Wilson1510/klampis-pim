from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.models.category_type_model import CategoryTypes
from app.schemas.category_type_schema import CategoryTypeCreate, CategoryTypeUpdate
from app.repositories.base import CRUDBase
from app.repositories.category_repository import category_repository


class CategoryTypeRepository(
    CRUDBase[CategoryTypes, CategoryTypeCreate, CategoryTypeUpdate]
):
    """Repository for CategoryType operations."""

    async def get_multi_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[CategoryTypes]:
        """Get category types with filtering support."""
        query = select(self.model)

        # Build filter conditions
        conditions = []

        if name is not None:
            conditions.append(self.model.name.ilike(f"%{name}%"))

        if slug is not None:
            conditions.append(self.model.slug == slug)

        if is_active is not None:
            conditions.append(self.model.is_active == is_active)

        # Apply filters if any
        if conditions:
            query = query.where(and_(*conditions))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_name(
        self, db: AsyncSession, name: str
    ) -> CategoryTypes | None:
        """Get category type by name."""
        query = select(self.model).where(self.model.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def count_categories(
        self, db: AsyncSession, category_type_id: int
    ) -> int:
        """Count categories associated with this category type."""
        # Import here to avoid circular import
        from app.models.category_model import Categories

        query = select(func.count(Categories.id)).where(
            and_(
                Categories.category_type_id == category_type_id,
                Categories.is_active.is_(True)
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0

    async def get_categories_by_type(
        self,
        db: AsyncSession,
        category_type_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get categories by category type."""
        # Import here to avoid circular import
        from app.models.category_model import Categories

        query = (
            select(Categories)
            .options(selectinload(Categories.category_type))
            .where(
                and_(
                    Categories.category_type_id == category_type_id,
                    Categories.is_active.is_(True)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        categories = result.scalars().all()
        for category in categories:
            await category_repository.load_children_recursively(db, category)
        return categories


# Create instance to be used as dependency
category_type_repository = CategoryTypeRepository(CategoryTypes)
