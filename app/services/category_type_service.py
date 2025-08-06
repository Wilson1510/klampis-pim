from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from fastapi import status

from app.repositories import category_type_repository
from app.models import CategoryTypes, Categories, Users
from app.schemas.category_type_schema import (
    CategoryTypeCreate,
    CategoryTypeUpdate
)
from app.api.v1.dependencies.auth import require_resource_ownership


class CategoryTypeService:
    """Service layer for CategoryType business logic."""

    def __init__(self):
        self.repository = category_type_repository

    async def get_all_category_types(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[CategoryTypes], int]:
        """Get all category types with pagination and total count."""
        data = await self.repository.get_multi(db, skip=skip, limit=limit)
        total = len(data)
        return data, total

    async def get_category_types_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[CategoryTypes], int]:
        """Get category types with filtering support and total count."""
        if name is None and slug is None and is_active is None:
            return await self.get_all_category_types(db, skip=skip, limit=limit)

        data = await self.repository.get_multi_with_filter(
            db,
            skip=skip,
            limit=limit,
            name=name,
            slug=slug,
            is_active=is_active
        )
        total = len(data)
        return data, total

    async def get_category_type_by_id(
        self, db: AsyncSession, category_type_id: int
    ) -> CategoryTypes | None:
        """Get category type by ID."""
        return await self.repository.get(db, id=category_type_id)

    async def create_category_type(
        self, db: AsyncSession, category_type_create: CategoryTypeCreate,
        created_by: int
    ) -> CategoryTypes:
        """Create a new category type."""
        # Check if category type with same name already exists
        existing = await self.repository.get_by_field(
            db, 'name', category_type_create.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Category type with name '{category_type_create.name}' "
                    "already exists"
                )
            )

        return await self.repository.create(
            db, obj_in=category_type_create, created_by=created_by
        )

    async def update_category_type(
        self,
        db: AsyncSession,
        category_type_id: int,
        category_type_update: CategoryTypeUpdate,
        updated_by: int,
        current_user: Users
    ) -> CategoryTypes:
        """Update an existing category type."""
        # Get existing category type
        db_category_type = await self.repository.get(db, id=category_type_id)
        if not db_category_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category type with id {category_type_id} not found"
            )

        # Check ownership - ADMIN/MANAGER/SYSTEM can update any, USER only their own
        require_resource_ownership(current_user, db_category_type.created_by)

        # Check if new name conflicts with existing category type
        if (
            category_type_update.name
            and category_type_update.name != db_category_type.name
        ):
            existing = await self.repository.get_by_field(
                db, 'name', category_type_update.name
            )
            if existing and existing.id != category_type_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Category type with name '{category_type_update.name}' "
                        "already exists"
                    )
                )

        return await self.repository.update(
            db, db_obj=db_category_type, obj_in=category_type_update,
            updated_by=updated_by
        )

    async def delete_category_type(
        self, db: AsyncSession, category_type_id: int, current_user: Users
    ) -> CategoryTypes:
        """Delete a category type."""
        db_category_type = await self.repository.get(db, id=category_type_id)
        if not db_category_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category type with id {category_type_id} not found"
            )

        # Check ownership - ADMIN/MANAGER/SYSTEM can delete any, USER only their own
        require_resource_ownership(current_user, db_category_type.created_by)

        # Check if category type has associated categories
        categories_count = await self.repository.count_children(
            db, 'category_type_id', category_type_id, Categories
        )
        if categories_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot delete category type. It has {categories_count} "
                    "associated categories"
                )
            )

        return await self.repository.delete(db, id=category_type_id)

    async def get_categories_by_type(
        self,
        db: AsyncSession,
        category_type_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List, int]:
        """Get all categories under a specific category type with total count."""
        # Verify category type exists
        category_type = await self.repository.get(db, id=category_type_id)
        if not category_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category type with id {category_type_id} not found"
            )

        data = await self.repository.get_categories_by_type(
            db, category_type_id=category_type_id, skip=skip, limit=limit
        )
        total = len(data)
        return data, total


# Create instance to be used as dependency
category_type_service = CategoryTypeService()
