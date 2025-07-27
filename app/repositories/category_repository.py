from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category_model import Categories
from app.schemas.category_schema import CategoryCreate, CategoryUpdate
from app.repositories.base import CRUDBase


class CategoryRepository(
    CRUDBase[Categories, CategoryCreate, CategoryUpdate]
):
    """Repository for Category operations."""
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
