from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from fastapi import status

from app.repositories import attribute_repository
from app.models import Attributes, SkuAttributeValue
from app.schemas.attribute_schema import (
    AttributeCreate,
    AttributeUpdate
)


class AttributeService:
    """Service layer for Attribute business logic."""

    def __init__(self):
        self.repository = attribute_repository

    async def get_all_attributes(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Attributes], int]:
        """Get all attributes with pagination and total count."""
        data = await self.repository.get_multi(db, skip=skip, limit=limit)
        total = len(data)
        return data, total

    async def get_attributes_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        code: Optional[str] = None,
        data_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Attributes], int]:
        """Get attributes with filtering support and total count."""
        if name is None and code is None and data_type is None and is_active is None:
            return await self.get_all_attributes(db, skip=skip, limit=limit)

        data = await self.repository.get_multi_with_filter(
            db,
            skip=skip,
            limit=limit,
            name=name,
            code=code,
            data_type=data_type,
            is_active=is_active
        )
        total = len(data)
        return data, total

    async def get_attribute_by_id(
        self, db: AsyncSession, attribute_id: int
    ) -> Attributes | None:
        """Get attribute by ID with all relationships."""
        return await self.repository.get(db, id=attribute_id)

    async def create_attribute(
        self, db: AsyncSession, attribute_create: AttributeCreate
    ) -> Attributes:
        """Create a new attribute."""
        # Check if attribute with same name already exists
        existing_name = await self.repository.get_by_field(
            db, 'name', attribute_create.name
        )
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Attribute with name '{attribute_create.name}' "
                    "already exists"
                )
            )

        return await self.repository.create(db, obj_in=attribute_create)

    async def update_attribute(
        self,
        db: AsyncSession,
        attribute_id: int,
        attribute_update: AttributeUpdate
    ) -> Attributes:
        """Update an existing attribute."""
        # Get existing attribute
        db_attribute = await self.repository.get(db, id=attribute_id)
        if not db_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute with id {attribute_id} not found"
            )

        # Check if new name conflicts with existing attribute
        if (
            attribute_update.name
            and attribute_update.name != db_attribute.name
        ):
            existing = await self.repository.get_by_field(
                db, 'name', attribute_update.name
            )
            if existing and existing.id != attribute_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Attribute with name '{attribute_update.name}' "
                        "already exists"
                    )
                )

        return await self.repository.update(
            db, db_obj=db_attribute, obj_in=attribute_update
        )

    async def delete_attribute(
        self, db: AsyncSession, attribute_id: int
    ) -> Attributes:
        """Delete an attribute."""
        db_attribute = await self.repository.get(db, id=attribute_id)
        if not db_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute with id {attribute_id} not found"
            )

        # Check if attribute has associated SKU attribute values
        sku_values_count = await self.repository.count_children(
            db, 'attribute_id', attribute_id, SkuAttributeValue
        )
        if sku_values_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot delete attribute. It has {sku_values_count} "
                    "associated SKU attribute values"
                )
            )

        return await self.repository.delete(db, id=attribute_id)


# Create instance to be used as dependency
attribute_service = AttributeService()
