from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models import Pricelists
from app.schemas.pricelist_schema import PricelistCreate, PricelistUpdate
from app.repositories.base import CRUDBase


class PricelistRepository(CRUDBase[Pricelists, PricelistCreate, PricelistUpdate]):
    """Repository for Pricelist operations."""

    async def get_multi_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        code: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Pricelists]:
        """Get pricelists with filtering support."""
        query = select(self.model)

        # Build filter conditions
        conditions = []

        if name is not None:
            conditions.append(self.model.name.ilike(f"%{name}%"))

        if code is not None:
            conditions.append(self.model.code.ilike(f"%{code}%"))

        if is_active is not None:
            conditions.append(self.model.is_active == is_active)

        # Apply filters if any
        if conditions:
            query = query.where(and_(*conditions))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()


# Create instance to be used as dependency
pricelist_repository = PricelistRepository(Pricelists)
