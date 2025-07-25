from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_type_repository import category_type_repository
from app.models.category_type_model import CategoryTypes


class CategoryTypeService:
    """Service layer for CategoryType business logic."""

    def __init__(self):
        self.repository = category_type_repository

    async def get_all_category_types(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[CategoryTypes]:
        """Get all category types with pagination."""
        return await self.repository.get_multi(db, skip=skip, limit=limit)

    async def get_category_type_by_id(
        self, db: AsyncSession, category_type_id: int
    ) -> CategoryTypes | None:
        """Get category type by ID."""
        return await self.repository.get(db, id=category_type_id)


# Create instance to be used as dependency
category_type_service = CategoryTypeService()
