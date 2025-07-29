from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from slugify import slugify

from app.repositories.category_repository import category_repository
from app.models.category_model import Categories
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate
)


class CategoryService:
    """Service layer for Category business logic."""

    def __init__(self):
        self.repository = category_repository

    async def get_all_categories(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Categories], int]:
        """Get all categories with pagination and total count."""
        data = await self.repository.get_multi(db, skip=skip, limit=limit)
        total = len(data)
        return data, total

    async def get_categories_with_filter(
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
    ) -> Tuple[List[Categories], int]:
        """Get categories with filtering support and total count."""
        if (
            name is None and slug is None and category_type_id is None
            and parent_id is None and is_active is None
        ):
            return await self.get_all_categories(db, skip=skip, limit=limit)

        data = await self.repository.get_multi_with_filter(
            db,
            skip=skip,
            limit=limit,
            name=name,
            slug=slug,
            category_type_id=category_type_id,
            parent_id=parent_id,
            is_active=is_active
        )
        total = len(data)
        return data, total

    async def get_category_by_id(
        self, db: AsyncSession, category_id: int
    ) -> Categories | None:
        """Get category by ID with all relations."""
        return await self.repository.get_with_full_relations(
            db, category_id=category_id
        )

    async def get_category_by_slug(
        self, db: AsyncSession, slug: str
    ) -> Categories | None:
        """Get category by slug with all relations."""
        return await self.repository.get_by_slug(db, slug=slug)

    async def get_top_level_categories(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Categories], int]:
        """Get all top-level categories with total count."""
        data = await self.repository.get_top_level_categories(
            db, skip=skip, limit=limit
        )
        total = len(data)
        return data, total

    async def get_children_by_parent(
        self,
        db: AsyncSession,
        parent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Categories], int]:
        """Get children of a specific category with total count."""
        # Verify parent exists
        parent = await self.repository.get(db, id=parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail=f"Parent category with id {parent_id} not found"
            )

        data = await self.repository.get_children_by_parent(
            db, parent_id=parent_id, skip=skip, limit=limit
        )
        total = len(data)
        return data, total

    async def create_category(
        self, db: AsyncSession, category_create: CategoryCreate
    ) -> Categories:
        """Create a new category with business validation."""
        # Generate slug from name
        slug = slugify(category_create.name)

        # Check if category with same slug already exists
        existing = await self.repository.get_by_slug(db, slug=slug)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Category with slug '{slug}' already exists"
            )

        # Validate hierarchy rules
        await self._validate_category_hierarchy(db, category_create)

        # Create the category using the repository with slug
        return await self.repository.create_with_slug(
            db, obj_in=category_create, slug=slug
        )

    async def update_category(
        self,
        db: AsyncSession,
        category_id: int,
        category_update: CategoryUpdate
    ) -> Categories:
        """Update an existing category with business validation."""
        # Get existing category
        db_category = await self.repository.get(db, id=category_id)
        if not db_category:
            raise HTTPException(
                status_code=404,
                detail=f"Category with id {category_id} not found"
            )

        # Generate new slug if name is being updated
        new_slug = None
        if category_update.name and category_update.name != db_category.name:
            new_slug = slugify(category_update.name)

            # Check if new slug conflicts with existing category
            existing = await self.repository.get_by_slug(db, slug=new_slug)
            if existing and existing.id != category_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Category with slug '{new_slug}' already exists"
                )

        # Validate hierarchy rules if parent_id or category_type_id is updated
        if (
            category_update.parent_id is not None or
            category_update.category_type_id is not None
        ):
            await self._validate_category_hierarchy_for_update(
                db, db_category, category_update
            )

        # Update with slug if needed
        if new_slug:
            return await self.repository.update_with_slug(
                db, db_obj=db_category, obj_in=category_update, slug=new_slug
            )
        else:
            return await self.repository.update(
                db, db_obj=db_category, obj_in=category_update
            )

    async def delete_category(
        self, db: AsyncSession, category_id: int
    ) -> Categories:
        """Soft delete a category after validation."""
        db_category = await self.repository.get(db, id=category_id)
        if not db_category:
            raise HTTPException(
                status_code=404,
                detail=f"Category with id {category_id} not found"
            )

        # Check if category has children
        children_count = await self.repository.count_children(db, category_id)
        if children_count > 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot delete category. It has {children_count} "
                    "child categories"
                )
            )

        # TODO: Check if category has associated products
        # This would require a product repository method

        return await self.repository.soft_delete(db, id=category_id)

    async def _validate_category_hierarchy(
        self, db: AsyncSession, category_create: CategoryCreate
    ) -> None:
        """Validate category hierarchy business rules."""
        parent_id = category_create.parent_id
        category_type_id = category_create.category_type_id

        # Rule 1: Top-level categories must have category_type_id
        if parent_id is None and category_type_id is None:
            raise HTTPException(
                status_code=400,
                detail="Top-level categories must have a category_type_id"
            )

        # Rule 2: Child categories must not have category_type_id
        if parent_id is not None and category_type_id is not None:
            raise HTTPException(
                status_code=400,
                detail="Child categories must not have a category_type_id"
            )

        # Validate parent exists if provided
        if parent_id is not None:
            parent_exists = await self.repository.validate_parent_exists(
                db, parent_id
            )
            if not parent_exists:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Parent category with id {parent_id} "
                        "not found or inactive"
                    )
                )

        # Validate category type exists if provided
        if category_type_id is not None:
            category_type_exists = (
                await self.repository.validate_category_type_exists(
                    db, category_type_id
                )
            )
            if not category_type_exists:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Category type with id {category_type_id} "
                        "not found or inactive"
                    )
                )

    async def _validate_category_hierarchy_for_update(
        self,
        db: AsyncSession,
        existing_category: Categories,
        category_update: CategoryUpdate
    ) -> None:
        """Validate category hierarchy rules for updates."""
        # Get current values or use existing ones
        parent_id = (
            category_update.parent_id
            if category_update.parent_id is not None
            else existing_category.parent_id
        )
        category_type_id = (
            category_update.category_type_id
            if category_update.category_type_id is not None
            else existing_category.category_type_id
        )

        # Apply the same hierarchy rules as create
        if parent_id is None and category_type_id is None:
            raise HTTPException(
                status_code=400,
                detail="Top-level categories must have a category_type_id"
            )

        if parent_id is not None and category_type_id is not None:
            raise HTTPException(
                status_code=400,
                detail="Child categories must not have a category_type_id"
            )

        # Validate parent exists if being updated
        if (
            category_update.parent_id is not None and
            category_update.parent_id != existing_category.parent_id
        ):
            parent_exists = await self.repository.validate_parent_exists(
                db, category_update.parent_id
            )
            if not parent_exists:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Parent category with id {category_update.parent_id} "
                        "not found or inactive"
                    )
                )

        # Validate category type exists if being updated
        if (
            category_update.category_type_id is not None and
            category_update.category_type_id != existing_category.category_type_id
        ):
            category_type_exists = (
                await self.repository.validate_category_type_exists(
                    db, category_update.category_type_id
                )
            )
            if not category_type_exists:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Category type with id "
                        f"{category_update.category_type_id} "
                        "not found or inactive"
                    )
                )


# Create instance to be used as dependency
category_service = CategoryService()
