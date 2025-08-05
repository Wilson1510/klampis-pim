from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models import Suppliers, Products
from app.schemas.supplier_schema import SupplierCreate, SupplierUpdate
from app.repositories.base import CRUDBase
from app.repositories import category_repository


class SupplierRepository(
    CRUDBase[Suppliers, SupplierCreate, SupplierUpdate]
):
    """Repository for Supplier operations."""

    async def get_multi_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        company_type: Optional[str] = None,
        email: Optional[str] = None,
        contact: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Suppliers]:
        """Get suppliers with filtering support."""
        query = select(self.model)

        # Build filter conditions
        conditions = []

        if name is not None:
            conditions.append(self.model.name.ilike(f"%{name}%"))

        if slug is not None:
            conditions.append(self.model.slug == slug)

        if company_type is not None:
            conditions.append(self.model.company_type == company_type)

        if email is not None:
            conditions.append(self.model.email.ilike(f"%{email}%"))

        if contact is not None:
            conditions.append(self.model.contact.ilike(f"%{contact}%"))

        if is_active is not None:
            conditions.append(self.model.is_active == is_active)

        # Apply filters if any
        if conditions:
            query = query.where(and_(*conditions))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_products_by_supplier(
        self, db: AsyncSession, supplier_id: int, skip: int = 0, limit: int = 100
    ) -> List[Products]:
        """Get products by supplier."""
        query = (
            select(Products)
            .options(
                selectinload(Products.category),
                selectinload(Products.images)
            )
            .where(Products.supplier_id == supplier_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        products = result.scalars().all()
        if len(products) > 0:
            await category_repository.load_parent_category_type_recursively(
                db, products[0].category
            )
        return products


# Create instance to be used as dependency
supplier_repository = SupplierRepository(Suppliers)
