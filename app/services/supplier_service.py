from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from fastapi import status

from app.repositories.supplier_repository import supplier_repository
from app.models import Suppliers, Products
from app.schemas.supplier_schema import (
    SupplierCreate,
    SupplierUpdate
)


class SupplierService:
    """Service layer for Supplier business logic."""

    def __init__(self):
        self.repository = supplier_repository

    async def get_all_suppliers(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Suppliers], int]:
        """Get all suppliers with pagination and total count."""
        data = await self.repository.get_multi(db, skip=skip, limit=limit)
        total = len(data)
        return data, total

    async def get_suppliers_with_filter(
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
    ) -> Tuple[List[Suppliers], int]:
        """Get suppliers with filtering support and total count."""
        if (
            name is None and slug is None and company_type is None
            and email is None and contact is None and is_active is None
        ):
            return await self.get_all_suppliers(db, skip=skip, limit=limit)

        data = await self.repository.get_multi_with_filter(
            db,
            skip=skip,
            limit=limit,
            name=name,
            slug=slug,
            company_type=company_type,
            email=email,
            contact=contact,
            is_active=is_active
        )
        total = len(data)
        return data, total

    async def get_supplier_by_id(
        self, db: AsyncSession, supplier_id: int
    ) -> Suppliers | None:
        """Get supplier by ID."""
        return await self.repository.get(db, id=supplier_id)

    async def get_products_by_supplier(
        self, db: AsyncSession, supplier_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Products], int]:
        """Get products by supplier with total count."""
        # Verify supplier exists
        supplier = await self.repository.get(db, id=supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with id {supplier_id} not found"
            )

        data = await self.repository.get_products_by_supplier(
            db, supplier_id=supplier_id, skip=skip, limit=limit
        )
        total = len(data)
        return data, total

    async def create_supplier(
        self, db: AsyncSession, supplier_create: SupplierCreate
    ) -> Suppliers:
        """Create a new supplier with business validation."""
        # Check if supplier with same name already exists
        existing_name = await self.repository.get_by_field(
            db, 'name', supplier_create.name
        )
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Supplier with name '{supplier_create.name}' already exists"
            )

        # Check if supplier with same email already exists
        existing_email = await self.repository.get_by_field(
            db, 'email', supplier_create.email
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Supplier with email '{supplier_create.email}' already exists"
                )
            )

        # Check if supplier with same contact already exists
        existing_contact = await self.repository.get_by_field(
            db, 'contact', supplier_create.contact
        )
        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Supplier with contact '{supplier_create.contact}' "
                    "already exists"
                )
            )

        return await self.repository.create(db, obj_in=supplier_create)

    async def update_supplier(
        self,
        db: AsyncSession,
        supplier_id: int,
        supplier_update: SupplierUpdate
    ) -> Suppliers:
        """Update an existing supplier with business validation."""
        # Get existing supplier
        db_supplier = await self.repository.get(db, id=supplier_id)
        if not db_supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with id {supplier_id} not found"
            )

        # Check for name conflicts if name is being updated
        if supplier_update.name and supplier_update.name != db_supplier.name:
            existing_name = await self.repository.get_by_field(
                db, 'name', supplier_update.name
            )
            if existing_name and existing_name.id != supplier_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Supplier with name '{supplier_update.name}' "
                        "already exists"
                    )
                )

        # Check for email conflicts if email is being updated
        if supplier_update.email and supplier_update.email != db_supplier.email:
            existing_email = await self.repository.get_by_field(
                db, 'email', supplier_update.email
            )
            if existing_email and existing_email.id != supplier_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Supplier with email '{supplier_update.email}' "
                        "already exists"
                    )
                )

        # Check for contact conflicts if contact is being updated
        if (
            supplier_update.contact and
            supplier_update.contact != db_supplier.contact
        ):
            existing_contact = await self.repository.get_by_field(
                db, 'contact', supplier_update.contact
            )
            if existing_contact and existing_contact.id != supplier_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Supplier with contact '{supplier_update.contact}' "
                        "already exists"
                    )
                )

        return await self.repository.update(
            db, db_obj=db_supplier, obj_in=supplier_update
        )

    async def delete_supplier(
        self, db: AsyncSession, supplier_id: int
    ) -> Suppliers:
        """Delete a supplier after validation."""
        db_supplier = await self.repository.get(db, id=supplier_id)
        if not db_supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with id {supplier_id} not found"
            )

        # Check if supplier has products
        products_count = await self.repository.count_children(
            db, 'supplier_id', supplier_id, Products
        )
        if products_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot delete supplier. It has {products_count} "
                    "products"
                )
            )

        return await self.repository.delete(db, id=supplier_id)


# Create instance to be used as dependency
supplier_service = SupplierService()
