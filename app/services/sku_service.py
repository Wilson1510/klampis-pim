from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories import sku_repository
from app.models import Skus, Attributes, Users
from app.schemas.sku_schema import SkuCreate, SkuUpdate, AttributeValueInput
from app.api.v1.dependencies.auth import require_resource_ownership


class SkuService:
    """Service layer for SKU business logic."""

    def __init__(self):
        self.repository = sku_repository

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
        self, db: AsyncSession, sku_create: SkuCreate, created_by: int
    ) -> Skus:
        """Create a new SKU with business validation."""

        existing = await self.repository.get_by_field(db, 'name', sku_create.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SKU with name '{sku_create.name}' already exists"
            )

        # Validate attributes exist and get their data types
        if sku_create.attribute_values:
            attribute_ids = [
                av.attribute_id for av in sku_create.attribute_values
            ]
            existing_attributes = await self.repository.get_existing_attributes(
                db, attribute_ids
            )

            existing_attribute_ids = {attr.id for attr in existing_attributes}

            missing_attribute_ids = set(attribute_ids) - existing_attribute_ids
            if missing_attribute_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Attributes with IDs {missing_attribute_ids} not found"
                )

            # Create attribute lookup for validation
            attr_lookup = {attr.id: attr for attr in existing_attributes}

            # Validate attribute values against their data types
            await self._validate_attribute_values(
                sku_create.attribute_values, attr_lookup
            )

        # Validate pricelists exist
        if sku_create.price_details:
            pricelist_ids = [
                pd.pricelist_id for pd in sku_create.price_details
            ]
            existing_pricelists = await self.repository.get_existing_pricelists(
                db, pricelist_ids
            )

            existing_pricelist_ids = {pl.id for pl in existing_pricelists}
            missing_pricelist_ids = set(pricelist_ids) - existing_pricelist_ids
            if missing_pricelist_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pricelists with IDs {missing_pricelist_ids} not found"
                )

        return await self.repository.create_sku(
            db, obj_in=sku_create, created_by=created_by
        )

    async def update_sku(
        self,
        db: AsyncSession,
        sku_id: int,
        sku_update: SkuUpdate,
        updated_by: int,
        current_user: Users
    ) -> Skus:
        """Update an existing SKU with business validation."""

        # Get existing SKU
        db_sku = await self.repository.get(db, id=sku_id)
        if not db_sku:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SKU with id {sku_id} not found"
            )

        # Check ownership - ADMIN/MANAGER/SYSTEM can update any, USER only their own
        require_resource_ownership(current_user, db_sku.created_by)

        # Validate name uniqueness within product if being updated
        if sku_update.name and sku_update.name != db_sku.name:
            existing = await self.repository.get_by_field(
                db, 'name', sku_update.name
            )
            if existing and existing.id != sku_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"SKU with name '{sku_update.name}' already exists"
                )

        # Validate attributes if being updated
        if sku_update.attribute_values:
            attribute_ids = [
                av.attribute_id for av in sku_update.attribute_values
            ]
            existing_attribute_values = await self.repository.\
                get_existing_attribute_values(
                    db, sku_id=sku_id, attribute_ids=attribute_ids
                )

            # aiesav = atribute ids of existing sku attribute values
            aiesav = {av.attribute_id for av in existing_attribute_values}
            maiesav = set(attribute_ids) - aiesav
            if maiesav:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Attribute values with sku id {sku_id} and attribute "
                        f"ids {maiesav} not found"
                    )
                )

            # Create attribute lookup for validation
            existing_attributes = await self.repository.get_existing_attributes(
                db, attribute_ids
            )
            attr_lookup = {attr.id: attr for attr in existing_attributes}

            # Validate attribute values against their data types
            await self._validate_attribute_values(
                sku_update.attribute_values, attr_lookup
            )

        if sku_update.price_details_to_create:
            pricelist_ids = [
                pd.pricelist_id for pd in sku_update.price_details_to_create
            ]
            existing_pricelists = await self.repository.get_existing_pricelists(
                db, pricelist_ids
            )

            existing_pricelist_ids = {pl.id for pl in existing_pricelists}
            missing_pricelist_ids = set(pricelist_ids) - existing_pricelist_ids
            if missing_pricelist_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pricelists with IDs {missing_pricelist_ids} not found"
                )

        return await self.repository.update_sku(
            db, db_sku, sku_update, updated_by=updated_by
        )

    async def delete_sku(
        self, db: AsyncSession, sku_id: int, current_user: Users
    ) -> Skus:
        """Delete a SKU after validation."""
        db_sku = await self.repository.get(db, id=sku_id)
        if not db_sku:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SKU with id {sku_id} not found"
            )

        # Check ownership - ADMIN/MANAGER/SYSTEM can delete any, USER only their own
        require_resource_ownership(current_user, db_sku.created_by)

        return await self.repository.delete(db, id=sku_id)

    async def _validate_attribute_values(
        self,
        attribute_values: List[AttributeValueInput],
        attr_lookup: dict[int, Attributes]
    ) -> None:
        """Validate attribute values against their data types (simple validation)."""
        for attr_value in attribute_values:
            attribute = attr_lookup.get(attr_value.attribute_id)

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
