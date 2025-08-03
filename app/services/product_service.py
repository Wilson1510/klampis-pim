from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from fastapi import status

from app.repositories import product_repository
from app.models import Products, Skus
from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate
)


class ProductService:
    """Service layer for Product business logic."""

    def __init__(self):
        self.repository = product_repository

    async def get_products_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        category_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Products], int]:
        """Get products with filtering support and total count."""
        data = await self.repository.get_multi_with_filter(
            db,
            skip=skip,
            limit=limit,
            name=name,
            slug=slug,
            category_id=category_id,
            supplier_id=supplier_id,
            is_active=is_active
        )
        total = len(data)
        return data, total

    async def get_product_by_id(
        self, db: AsyncSession, product_id: int
    ) -> Products | None:
        """Get product by ID with all relationships."""
        return await self.repository.get_with_relationships(db, product_id=product_id)

    async def get_skus_by_product(
        self, db: AsyncSession, product_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Skus], int]:
        """Get SKUs by product with total count."""
        # Verify product exists
        product = await self.repository.get(db, id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )

        data = await self.repository.get_skus_by_product(
            db, product_id=product_id, skip=skip, limit=limit
        )
        total = len(data)
        return data, total

    async def create_product(
        self, db: AsyncSession, product_create: ProductCreate
    ) -> Products:
        """Create a new product with business validation."""

        # Validate name uniqueness
        existing = await self.repository.get_by_field(db, 'name', product_create.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with name '{product_create.name}' already exists"
            )

        data = await self.repository.create_product(db, obj_in=product_create)
        return data

    async def update_product(
        self,
        db: AsyncSession,
        product_id: int,
        product_update: ProductUpdate
    ) -> Products:
        """Update an existing product with business validation."""

        # Get existing product
        db_product = await self.repository.get(db, id=product_id)
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )

        # Validate name uniqueness if being updated
        if product_update.name and product_update.name != db_product.name:
            existing = await self.repository.get_by_field(
                db, 'name', product_update.name
            )
            if existing and existing.id != product_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with name '{product_update.name}' already exists"
                )

        return await self.repository.update_product(
            db, db_obj=db_product, obj_in=product_update
        )

    async def delete_product(self, db: AsyncSession, product_id: int) -> None:
        """Delete a product."""

        # Get existing product
        db_product = await self.repository.get(db, id=product_id)
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )

        # Check if product has SKUs
        sku_count = await self.repository.count_children(
            db, 'product_id', product_id, Skus
        )
        if sku_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot delete product. It has {sku_count} "
                    "SKUs"
                )
            )

        await self.repository.delete(db, id=product_id)


# Create the service instance
product_service = ProductService()
