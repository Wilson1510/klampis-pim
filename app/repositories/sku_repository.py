from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import (
    Skus, Products, Attributes, PriceDetails, SkuAttributeValue, Pricelists
)
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

    async def get_existing_attributes(
        self, db: AsyncSession, attribute_ids: List[int]
    ) -> List[Attributes]:
        """Validate that all attributes exist and return them."""
        query = select(Attributes).where(and_(
            Attributes.id.in_(attribute_ids),
            Attributes.is_active is True
        ))
        result = await db.execute(query)
        attributes = result.scalars().all()

        return attributes

    async def get_existing_pricelists(
        self, db: AsyncSession, pricelist_ids: List[int]
    ) -> List[Pricelists]:
        """Validate that all pricelists exist and return them."""
        query = select(Pricelists).where(and_(
            Pricelists.id.in_(pricelist_ids),
            Pricelists.is_active is True
        ))
        result = await db.execute(query)
        pricelists = result.scalars().all()
        return pricelists

    async def create_sku(
        self, db: AsyncSession, obj_in: SkuCreate
    ) -> Skus:
        """Create SKU with price details and attribute values."""
        # Create the main SKU object
        sku_data = obj_in.model_dump(
            exclude={'price_details', 'attribute_values'}
        )
        db_sku = await super().create(db, obj_in=sku_data)

        try:
            # Create price details
            for price_detail_data in obj_in.price_details:
                price_detail = PriceDetails(
                    sku_id=db_sku.id,
                    **price_detail_data.model_dump()
                )
                db.add(price_detail)

            # Create attribute values
            for attr_value_data in obj_in.attribute_values:
                attr_value = SkuAttributeValue(
                    sku_id=db_sku.id,
                    **attr_value_data.model_dump()
                )
                db.add(attr_value)

            await db.commit()
            return await self.get_with_relationships(db, db_sku.id)

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to create price details or attribute values: {str(e)}"
            )

    async def update_sku(
        self, db: AsyncSession, db_obj: Skus, obj_in: SkuUpdate
    ) -> Skus:
        """Update SKU with price details and attribute values."""
        # Update basic SKU fields
        update_data = obj_in.model_dump(
            exclude={
                'price_details_to_create',
                'price_details_to_update',
                'price_details_to_delete',
                'attribute_values'
            }
        )
        await super().update(db, db_obj=db_obj, obj_in=update_data)

        try:
            # Handle price details updates
            if obj_in.price_details_to_delete:
                # Delete price details
                for price_detail_id in obj_in.price_details_to_delete:
                    price_detail = await db.get(PriceDetails, price_detail_id)
                    if price_detail and price_detail.sku_id == db_obj.id:
                        price_detail.is_active = False
                        db.add(price_detail)
                    elif not price_detail:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Price detail with ID {price_detail_id} not found"
                        )
                    elif price_detail.sku_id != db_obj.id:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Price detail with ID {price_detail_id} does not "
                                f"belong to SKU {db_obj.id}"
                            )
                        )

            if obj_in.price_details_to_create:
                for price_detail_data in obj_in.price_details_to_create:
                    price_detail_to_create = PriceDetails(
                        sku_id=db_obj.id,
                        **price_detail_data.model_dump()
                    )
                    db.add(price_detail_to_create)

            if obj_in.price_details_to_update:
                for price_detail_update in obj_in.price_details_to_update:
                    price_detail = await db.get(
                        PriceDetails, price_detail_update.id
                    )
                    if price_detail and price_detail.sku_id == db_obj.id:
                        update_price_data = price_detail_update.model_dump(
                            exclude_unset=True, exclude={'id'}
                        )
                        for field, value in update_price_data.items():
                            setattr(price_detail, field, value)
                        db.add(price_detail)
                    elif not price_detail:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Price detail with ID {price_detail_id} not found"
                        )
                    elif price_detail.sku_id != db_obj.id:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Price detail with ID {price_detail_id} does not "
                                f"belong to SKU {db_obj.id}"
                            )
                        )

            # Handle attribute values updates
            if obj_in.attribute_values:
                for attr_value_data in obj_in.attribute_values:
                    query = (
                        select(SkuAttributeValue)
                        .where(
                            and_(
                                SkuAttributeValue.sku_id == db_obj.id,
                                SkuAttributeValue.attribute_id == (
                                    attr_value_data.attribute_id
                                )
                            )
                        )
                    )
                    result = await db.execute(query)
                    existing_attr_value = result.scalar_one()
                    existing_attr_value.value = attr_value_data.value
                    db.add(existing_attr_value)

            await db.commit()
            return await self.get_with_relationships(db, db_obj.id)

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to update SKU: {str(e)}"
            )


# Create instance to be used as dependency
sku_repository = SkuRepository(Skus)
