from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import Skus, Products, Attributes, PriceDetails, SkuAttributeValue
from app.schemas.sku_schema import SkuCreate, SkuUpdate
from app.repositories.base import CRUDBase


class SkuRepository(CRUDBase[Skus, SkuCreate, SkuUpdate]):
    """Repository for SKU operations with complex relationships."""

    async def get_multi_with_filter(
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
    ) -> List[Skus]:
        """Get SKUs with filtering support."""
        query = select(self.model).options(
            selectinload(self.model.product).selectinload(Products.category),
            selectinload(self.model.price_details).selectinload(
                PriceDetails.pricelist
            ),
            selectinload(self.model.sku_attribute_values).selectinload(
                SkuAttributeValue.attribute
            )
        )

        # Build filter conditions
        conditions = []

        if name is not None:
            conditions.append(self.model.name.ilike(f"%{name}%"))

        if slug is not None:
            conditions.append(self.model.slug == slug)

        if sku_number is not None:
            conditions.append(self.model.sku_number == sku_number)

        if product_id is not None:
            conditions.append(self.model.product_id == product_id)

        if is_active is not None:
            conditions.append(self.model.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_relationships(
        self, db: AsyncSession, sku_id: int
    ) -> Optional[Skus]:
        """Get SKU with all its relationships loaded."""
        query = select(self.model).options(
            selectinload(self.model.product).selectinload(Products.category),
            selectinload(self.model.price_details).selectinload(
                PriceDetails.pricelist
            ),
            selectinload(self.model.sku_attribute_values).selectinload(
                SkuAttributeValue.attribute
            )
        ).where(self.model.id == sku_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def validate_attributes_exist(
        self, db: AsyncSession, attribute_ids: List[int]
    ) -> List[Attributes]:
        """Validate that all attributes exist and return them."""
        result = await db.execute(
            select(Attributes)
            .where(and_(
                Attributes.id.in_(attribute_ids),
                Attributes.is_active is True
            ))
        )
        attributes = result.scalars().all()

        found_ids = {attr.id for attr in attributes}
        missing_ids = set(attribute_ids) - found_ids

        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Attributes with IDs {list(missing_ids)} "
                    "not found or inactive"
                )
            )

        return attributes

    async def create_sku_with_relationships(
        self, db: AsyncSession, sku_create: SkuCreate
    ) -> Skus:
        """Create SKU with price details and attribute values."""
        try:
            # Create the main SKU object
            sku_data = sku_create.model_dump(
                exclude={'price_details', 'attribute_values'}
            )
            db_sku = self.model(**sku_data)
            db.add(db_sku)
            await db.flush()  # Get the ID without committing

            # Create price details
            for price_detail_data in sku_create.price_details:
                price_detail = PriceDetails(
                    sku_id=db_sku.id,
                    **price_detail_data.model_dump()
                )
                db.add(price_detail)

            # Create attribute values
            for attr_value_data in sku_create.attribute_values:
                attr_value = SkuAttributeValue(
                    sku_id=db_sku.id,
                    **attr_value_data.model_dump()
                )
                db.add(attr_value)

            await db.commit()
            await db.refresh(db_sku)
            return await self.get_with_relationships(db, db_sku.id)

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to create SKU: {str(e)}"
            )

    async def update_sku_with_relationships(
        self, db: AsyncSession, db_sku: Skus, sku_update: SkuUpdate
    ) -> Skus:
        """Update SKU with price details and attribute values."""
        try:
            # Update basic SKU fields
            update_data = sku_update.model_dump(
                exclude_unset=True,
                exclude={
                    'price_details_to_create',
                    'price_details_to_update',
                    'price_details_to_delete',
                    'attribute_values'
                }
            )

            for field, value in update_data.items():
                setattr(db_sku, field, value)

            # Handle price details updates
            if sku_update.price_details_to_delete:
                await db.execute(
                    select(PriceDetails).where(
                        and_(
                            PriceDetails.id.in_(
                                sku_update.price_details_to_delete
                            ),
                            PriceDetails.sku_id == db_sku.id
                        )
                    )
                )
                # Delete price details
                for price_detail_id in sku_update.price_details_to_delete:
                    price_detail = await db.get(PriceDetails, price_detail_id)
                    if price_detail and price_detail.sku_id == db_sku.id:
                        await db.delete(price_detail)

            if sku_update.price_details_to_create:
                for price_detail_data in sku_update.price_details_to_create:
                    price_detail = PriceDetails(
                        sku_id=db_sku.id,
                        **price_detail_data.model_dump()
                    )
                    db.add(price_detail)

            if sku_update.price_details_to_update:
                for price_detail_update in sku_update.price_details_to_update:
                    price_detail = await db.get(
                        PriceDetails, price_detail_update.id
                    )
                    if price_detail and price_detail.sku_id == db_sku.id:
                        update_price_data = price_detail_update.model_dump(
                            exclude_unset=True, exclude={'id'}
                        )
                        for field, value in update_price_data.items():
                            setattr(price_detail, field, value)

            # Handle attribute values updates
            if sku_update.attribute_values is not None:
                # Delete existing attribute values
                result = await db.execute(
                    select(SkuAttributeValue).where(
                        SkuAttributeValue.sku_id == db_sku.id
                    )
                )
                existing_attr_values = result.scalars().all()
                for attr_value in existing_attr_values:
                    await db.delete(attr_value)

                # Create new attribute values
                for attr_value_data in sku_update.attribute_values:
                    attr_value = SkuAttributeValue(
                        sku_id=db_sku.id,
                        **attr_value_data.model_dump()
                    )
                    db.add(attr_value)

            await db.commit()
            await db.refresh(db_sku)
            return await self.get_with_relationships(db, db_sku.id)

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to update SKU: {str(e)}"
            )


# Create instance to be used as dependency
sku_repository = SkuRepository(Skus)
