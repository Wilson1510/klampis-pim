from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.sku_repository import sku_repository
from app.models import Skus, Attributes
from app.schemas.sku_schema import SkuCreate, SkuUpdate, AttributeValueInput


class SkuService:
    """Service layer for SKU business logic."""

    def __init__(self):
        self.repository = sku_repository

    async def get_all_skus(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Skus], int]:
        """Get all SKUs with pagination and total count."""
        data = await self.repository.get_multi(db, skip=skip, limit=limit)
        total = len(data)
        return data, total

    async def get_skus_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        sku_number: Optional[str] = None,
        product_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Skus], int]:
        """Get SKUs with filtering support and total count."""
        if (
            name is None and slug is None and sku_number is None
            and product_id is None and is_active is None
        ):
            return await self.get_all_skus(db, skip=skip, limit=limit)

        data = await self.repository.get_multi_with_filter(
            db,
            skip=skip,
            limit=limit,
            name=name,
            slug=slug,
            sku_number=sku_number,
            product_id=product_id,
            is_active=is_active
        )
        total = len(data)
        return data, total

    async def get_sku_by_id(
        self, db: AsyncSession, sku_id: int
    ) -> Skus | None:
        """Get SKU by ID with all relationships."""
        return await self.repository.get_with_relationships(db, sku_id=sku_id)

    async def create_sku(
        self, db: AsyncSession, sku_create: SkuCreate
    ) -> Skus:
        """Create a new SKU with business validation."""

        existing = await self.repository.get_by_field(db, 'name', sku_create.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"SKU with name '{sku_create.name}' already exists"
            )

        # Validate attributes exist and get their data types
        if sku_create.attribute_values:
            attribute_ids = [
                av.attribute_id for av in sku_create.attribute_values
            ]
            attributes = await self.repository.validate_attributes_exist(
                db, attribute_ids
            )

            # Create attribute lookup for validation
            attr_lookup = {attr.id: attr for attr in attributes}

            # Validate attribute values against their data types
            await self._validate_attribute_values(
                sku_create.attribute_values, attr_lookup
            )

        return await self.repository.create_sku_with_relationships(db, sku_create)

    async def update_sku(
        self,
        db: AsyncSession,
        sku_id: int,
        sku_update: SkuUpdate
    ) -> Skus:
        """Update an existing SKU with business validation."""

        # Get existing SKU
        db_sku = await self.repository.get(db, id=sku_id)
        if not db_sku:
            raise HTTPException(
                status_code=404,
                detail=f"SKU with id {sku_id} not found"
            )

        # Validate name uniqueness within product if being updated
        if sku_update.name and sku_update.name != db_sku.name:
            existing = await self.repository.get_by_field(
                db, 'name', sku_update.name
            )
            if existing and existing.id != sku_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"SKU with name '{sku_update.name}' already exists"
                )

        # Validate attributes if being updated
        if sku_update.attribute_values is not None:
            if sku_update.attribute_values:  # Not empty list
                attribute_ids = [
                    av.attribute_id for av in sku_update.attribute_values
                ]
                attributes = await self.repository.validate_attributes_exist(
                    db, attribute_ids
                )

                # Create attribute lookup for validation
                attr_lookup = {attr.id: attr for attr in attributes}

                # Validate attribute values against their data types
                await self._validate_attribute_values(
                    sku_update.attribute_values, attr_lookup
                )

        return await self.repository.update_sku_with_relationships(
            db, db_sku, sku_update
        )

    async def delete_sku(
        self, db: AsyncSession, sku_id: int
    ) -> Skus:
        """Soft delete a SKU after validation."""
        db_sku = await self.repository.get(db, id=sku_id)
        if not db_sku:
            raise HTTPException(
                status_code=404,
                detail=f"SKU with id {sku_id} not found"
            )

        return await self.repository.soft_delete(db, id=sku_id)

    async def _validate_attribute_values(
        self,
        attribute_values: List[AttributeValueInput],
        attr_lookup: dict[int, Attributes]
    ) -> None:
        """Validate attribute values against their data types (simple validation)."""
        for attr_value in attribute_values:
            attribute = attr_lookup.get(attr_value.attribute_id)
            if not attribute:
                continue  # Already validated in validate_attributes_exist

            # Simple data type validation
            is_valid = Attributes.validate_value_for_data_type(
                attr_value.value, attribute.data_type
            )

            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Invalid value '{attr_value.value}' for attribute "
                        f"'{attribute.name}' (expected {attribute.data_type.value})"
                    )
                )


# Create instance to be used as dependency
sku_service = SkuService()
