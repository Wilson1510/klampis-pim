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
from app.repositories import category_repository


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
        data = result.scalars().all()
        for sku in data:
            await category_repository.load_parent_category_type_recursively(
                db, sku.product.category
            )
        return data

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
        sku = result.scalar_one_or_none()

        if sku:
            await category_repository.load_parent_category_type_recursively(
                db, sku.product.category
            )
        return sku

    async def get_existing_attributes(
        self, db: AsyncSession, attribute_ids: List[int]
    ) -> List[Attributes]:
        """Validate that all attributes exist and return them."""
        query = select(Attributes).where(Attributes.id.in_(attribute_ids))
        result = await db.execute(query)
        attributes = result.scalars().all()
        return attributes

    async def get_existing_attribute_values(
        self, db: AsyncSession, sku_id: int, attribute_ids: List[int]
    ) -> List[SkuAttributeValue]:
        """Validate that all attribute values exist and return them."""
        query = select(SkuAttributeValue).where(and_(
            SkuAttributeValue.sku_id == sku_id,
            SkuAttributeValue.attribute_id.in_(attribute_ids),
        ))
        result = await db.execute(query)
        attribute_values = result.scalars().all()
        return attribute_values

    async def get_existing_pricelists(
        self, db: AsyncSession, pricelist_ids: List[int]
    ) -> List[Pricelists]:
        """Validate that all pricelists exist and return them."""
        query = select(Pricelists).where(Pricelists.id.in_(pricelist_ids))
        result = await db.execute(query)
        pricelists = result.scalars().all()
        return pricelists

    async def create_sku(
        self, db: AsyncSession, obj_in: SkuCreate, created_by: int
    ) -> Skus:
        """Create SKU with price details and attribute values."""
        try:
            # Create the main SKU object
            sku_data = obj_in.model_dump(
                exclude={'price_details', 'attribute_values'}
            )
            sku_data['created_by'] = created_by
            sku_data['updated_by'] = created_by
            await self.validate_foreign_key(
                db, Products, sku_data['product_id']
            )
            db_sku = Skus(**sku_data)
            db.add(db_sku)
            await db.commit()
            await db.refresh(db_sku)

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

        except HTTPException:
            # Re-raise HTTPException as-is (business logic errors)
            await db.rollback()
            raise
        except (ValueError, TypeError) as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
        except Exception as e:
            # Handle unexpected database/system errors
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create price details or attribute values: {str(e)}"
            )

    async def update_sku(
        self, db: AsyncSession, db_obj: Skus, obj_in: SkuUpdate, updated_by: int
    ) -> Skus:
        """Update SKU with price details and attribute values."""
        obj_data = db_obj.__dict__
        # Update basic SKU fields
        update_data = obj_in.model_dump(
            exclude_unset=True,
            exclude={
                'price_details_to_create',
                'price_details_to_update',
                'price_details_to_delete',
                'attribute_values'
            }
        )
        update_data['updated_by'] = updated_by

        try:
            if update_data:
                if 'product_id' in update_data:
                    await self.validate_foreign_key(
                        db, Products, update_data['product_id']
                    )
                for field in obj_data:
                    if field in update_data:
                        setattr(db_obj, field, update_data[field])
                db.add(db_obj)
                await db.commit()
                await db.refresh(db_obj)
            # Handle price details updates
            if obj_in.price_details_to_delete:
                # Validate that SKU will still have active price details after deletion
                await self._validate_price_details_deletion(
                    db, db_obj.id, obj_in.price_details_to_delete
                )

                # Delete price details
                for price_detail_id in obj_in.price_details_to_delete:
                    price_detail = await db.get(PriceDetails, price_detail_id)
                    if price_detail and price_detail.sku_id == db_obj.id:
                        await db.delete(price_detail)
                    elif not price_detail:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=(
                                f"Price detail with ID {price_detail_id} not found"
                            )
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
                            detail=(
                                f"Price detail with ID {price_detail_update.id} "
                                "not found"
                            )
                        )
                    elif price_detail.sku_id != db_obj.id:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Price detail with ID {price_detail_update.id} "
                                f"does not belong to SKU {db_obj.id}"
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

        except HTTPException:
            # Re-raise HTTPException as-is (business logic errors)
            await db.rollback()
            raise
        except Exception as e:
            # Handle unexpected database/system errors
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update SKU: {str(e)}"
            )

    async def _validate_price_details_deletion(
        self,
        db: AsyncSession,
        sku_id: int,
        price_details_to_delete: List[int]
    ) -> None:
        """
        Validate that SKU will still have active price details after deletion.

        Args:
            db: Database session
            sku_id: SKU ID
            price_details_to_delete: List of price detail IDs to be deleted

        Raises:
            HTTPException: If deletion would leave SKU without price details
        """
        # Get all active price details for this SKU
        query = select(PriceDetails).where(PriceDetails.sku_id == sku_id)
        result = await db.execute(query)
        current_price_details = result.scalars().all()

        if not current_price_details:
            return

        # Calculate remaining price details after deletion
        remaining_count = len([
            pd for pd in current_price_details
            if pd.id not in price_details_to_delete
        ])

        if remaining_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot delete price details. SKU {sku_id} must have "
                    "at least one active price detail"
                )
            )


# Create instance to be used as dependency
sku_repository = SkuRepository(Skus)
