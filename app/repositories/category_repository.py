from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.models import Categories, Products
from app.schemas.category_schema import CategoryCreate, CategoryUpdate
from app.repositories.base import CRUDBase


class CategoryRepository(
    CRUDBase[Categories, CategoryCreate, CategoryUpdate]
):
    """Repository for Category operations."""

    async def get_multi_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        category_type_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[Categories]:
        """Get categories with filtering support."""
        query = select(self.model).options(
            selectinload(self.model.category_type),
            selectinload(self.model.parent),
            selectinload(self.model.images)
        )

        # Build filter conditions
        conditions = []

        if name is not None:
            conditions.append(self.model.name.ilike(f"%{name}%"))

        if slug is not None:
            conditions.append(self.model.slug == slug)

        if category_type_id is not None:
            conditions.append(self.model.category_type_id == category_type_id)

        if parent_id is not None:
            conditions.append(self.model.parent_id == parent_id)

        if is_active is not None:
            conditions.append(self.model.is_active == is_active)

        # Apply filters if any
        if conditions:
            query = query.where(and_(*conditions))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        categories = result.scalars().all()

        # Load children recursively for each category
        for category in categories:
            await self.load_children_recursively(db, category)
            if category.parent is not None:
                await self.load_parent_category_type_recursively(db, category.parent)

        return categories

    async def get_by_name(
        self, db: AsyncSession, name: str
    ) -> Categories | None:
        """Get category by name."""
        query = select(self.model).where(self.model.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_children_by_parent(
        self,
        db: AsyncSession,
        parent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Categories]:
        """Get all direct children of a category."""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.parent),
                selectinload(self.model.images)
            )
            .where(
                and_(
                    self.model.parent_id == parent_id,
                    self.model.is_active.is_(True)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        categories = result.scalars().all()

        # Load children recursively for each category
        for category in categories:
            await self.load_children_recursively(db, category)
            await self.load_parent_category_type_recursively(db, category)

        return categories

    async def get_products_by_category(
        self, db: AsyncSession, category_id: int, skip: int = 0, limit: int = 100
    ) -> List[Products]:
        """Get products by category."""
        query = (
            select(Products)
            .options(
                selectinload(Products.category),
                selectinload(Products.images)
            )
            .where(
                and_(
                    Products.category_id == category_id,
                    Products.is_active.is_(True)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        products = result.scalars().all()
        if len(products) > 0:
            await self.load_parent_category_type_recursively(db, products[0].category)
        return products

    async def create_category(
        self, db: AsyncSession, obj_in: CategoryCreate
    ) -> Categories:
        """Create a new category."""
        data = await super().create(db, obj_in=obj_in)
        await self.load_children_recursively(db, data)
        await db.refresh(data, ['images'])
        await self.load_parent_category_type_recursively(db, data)
        return data

    async def update_category(
        self, db: AsyncSession, db_obj: Categories, obj_in: CategoryUpdate
    ) -> Categories:
        """Update an existing category."""
        data = await super().update(db, db_obj=db_obj, obj_in=obj_in)
        await self.load_children_recursively(db, data)
        await db.refresh(data, ['images'])
        await self.load_parent_category_type_recursively(db, data)
        return data

    async def count_children(
        self, db: AsyncSession, parent_id: int
    ) -> int:
        """Count direct children of a category."""
        query = select(func.count(self.model.id)).where(
            and_(
                self.model.parent_id == parent_id,
                self.model.is_active.is_(True)
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0

    async def count_products(
        self, db: AsyncSession, category_id: int
    ) -> int:
        """Count products by category."""
        query = select(func.count(Products.id)).where(
            and_(
                Products.category_id == category_id,
                Products.is_active.is_(True)
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0

    async def validate_parent_exists(
        self, db: AsyncSession, parent_id: int
    ) -> bool:
        """Check if parent category exists and is active."""
        query = select(func.count(self.model.id)).where(
            and_(
                self.model.id == parent_id,
                self.model.is_active.is_(True)
            )
        )
        result = await db.execute(query)
        return (result.scalar() or 0) > 0

    async def validate_category_type_exists(
        self, db: AsyncSession, category_type_id: int
    ) -> bool:
        """Check if category type exists and is active."""
        from app.models.category_type_model import CategoryTypes

        query = select(func.count(CategoryTypes.id)).where(
            and_(
                CategoryTypes.id == category_type_id,
                CategoryTypes.is_active.is_(True)
            )
        )
        result = await db.execute(query)
        return (result.scalar() or 0) > 0

    async def get_with_full_relations(
        self, db: AsyncSession, category_id: int
    ) -> Categories | None:
        """Get category with all relations loaded."""
        query = select(self.model).options(
            selectinload(self.model.category_type),
            selectinload(self.model.parent),
            selectinload(self.model.images)
        ).where(self.model.id == category_id)

        result = await db.execute(query)
        category = result.scalar_one_or_none()

        if category:
            await self.load_children_recursively(db, category)
            await self.load_parent_category_type_recursively(db, category)

        return category

    async def load_parent_category_type_recursively(
        self, session: AsyncSession, category: Categories
    ) -> None:
        """
        Load parent category type recursively. This will be used mostly for
        getting the category type of the parent category to be used for full path.
        """
        stmt = select(Categories).where(Categories.id == category.id).options(
            selectinload(Categories.category_type),
            selectinload(Categories.parent)
        )
        result = await session.execute(stmt)
        data = result.scalar_one_or_none()
        if data.parent is not None:
            await self.load_parent_category_type_recursively(session, data.parent)

    async def load_children_recursively(
        self, session: AsyncSession, category: Categories
    ) -> None:
        """
        Load all children recursively.
        Warning: This will cause N+1 query problem.
        """
        await session.refresh(category, ['children'])
        for child in category.children:
            await self.load_children_recursively(session, child)


# Create instance to be used as dependency
category_repository = CategoryRepository(Categories)
