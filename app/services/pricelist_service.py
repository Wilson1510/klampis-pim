from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from fastapi import status

from app.repositories import pricelist_repository
from app.models import Pricelists, PriceDetails
from app.schemas.pricelist_schema import (
    PricelistCreate,
    PricelistUpdate
)


class PricelistService:
    """Service layer for Pricelist business logic."""

    def __init__(self):
        self.repository = pricelist_repository

    async def get_all_pricelists(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Pricelists], int]:
        """Get all pricelists with pagination and total count."""
        data = await self.repository.get_multi(db, skip=skip, limit=limit)
        total = len(data)
        return data, total

    async def get_pricelists_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        code: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Pricelists], int]:
        """Get pricelists with filtering support and total count."""
        if name is None and code is None and is_active is None:
            return await self.get_all_pricelists(db, skip=skip, limit=limit)

        data = await self.repository.get_multi_with_filter(
            db,
            skip=skip,
            limit=limit,
            name=name,
            code=code,
            is_active=is_active
        )
        total = len(data)
        return data, total

    async def get_pricelist_by_id(
        self, db: AsyncSession, pricelist_id: int
    ) -> Pricelists | None:
        """Get pricelist by ID."""
        return await self.repository.get(db, id=pricelist_id)

    async def create_pricelist(
        self, db: AsyncSession, pricelist_create: PricelistCreate
    ) -> Pricelists:
        """Create a new pricelist."""
        # Check if pricelist with same name already exists
        existing = await self.repository.get_by_field(
            db, 'name', pricelist_create.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Pricelist with name '{pricelist_create.name}' "
                    "already exists"
                )
            )

        return await self.repository.create(db, obj_in=pricelist_create)

    async def update_pricelist(
        self,
        db: AsyncSession,
        pricelist_id: int,
        pricelist_update: PricelistUpdate
    ) -> Pricelists:
        """Update an existing pricelist."""
        # Get existing pricelist
        db_pricelist = await self.repository.get(db, id=pricelist_id)
        if not db_pricelist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pricelist with id {pricelist_id} not found"
            )

        # Check if new name conflicts with existing pricelist
        if (
            pricelist_update.name
            and pricelist_update.name != db_pricelist.name
        ):
            existing = await self.repository.get_by_field(
                db, 'name', pricelist_update.name
            )
            if existing and existing.id != pricelist_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Pricelist with name '{pricelist_update.name}' "
                        "already exists"
                    )
                )

        return await self.repository.update(
            db, db_obj=db_pricelist, obj_in=pricelist_update
        )

    async def delete_pricelist(
        self, db: AsyncSession, pricelist_id: int
    ) -> Pricelists:
        """Delete a pricelist."""
        db_pricelist = await self.repository.get(db, id=pricelist_id)
        if not db_pricelist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pricelist with id {pricelist_id} not found"
            )

        # Check if pricelist has associated price details
        price_details_count = await self.repository.count_children(
            db, 'pricelist_id', pricelist_id, PriceDetails
        )
        if price_details_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot delete pricelist. It has {price_details_count} "
                    "associated price details"
                )
            )

        return await self.repository.delete(db, id=pricelist_id)


# Create instance to be used as dependency
pricelist_service = PricelistService()
