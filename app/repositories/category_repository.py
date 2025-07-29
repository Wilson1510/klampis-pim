from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.models.category_model import Categories
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

        return categories

    async def get_by_slug(
        self, db: AsyncSession, slug: str
    ) -> Categories | None:
        """Get category by slug."""
        query = select(self.model).options(
            selectinload(self.model.category_type),
            selectinload(self.model.parent),
            selectinload(self.model.images)
        ).where(self.model.slug == slug)
        result = await db.execute(query)
        category = result.scalar_one_or_none()

        if category:
            await self.load_children_recursively(db, category)

        return category

    async def get_by_name(
        self, db: AsyncSession, name: str
    ) -> Categories | None:
        """Get category by name."""
        query = select(self.model).where(self.model.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_top_level_categories(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Categories]:
        """Get all top-level categories (parent_id is NULL)."""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.category_type),
                selectinload(self.model.images)
            )
            .where(
                and_(
                    self.model.parent_id.is_(None),
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

        return categories

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

        return categories

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

        return category

    async def create_with_slug(
        self, db: AsyncSession, *, obj_in: CategoryCreate, slug: str
    ) -> Categories:
        """Create a new category with generated slug."""
        obj_data = obj_in.model_dump()
        obj_data['slug'] = slug
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_with_slug(
        self,
        db: AsyncSession,
        *,
        db_obj: Categories,
        obj_in: CategoryUpdate,
        slug: str
    ) -> Categories:
        """Update a category with new slug."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        obj_data['slug'] = slug

        for field, value in obj_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

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
