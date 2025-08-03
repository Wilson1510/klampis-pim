from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import (
    Products,
    Images,
    Categories,
    Suppliers,
    Skus,
    PriceDetails,
    SkuAttributeValue,
)
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.repositories.base import CRUDBase
from app.repositories.category_repository import category_repository


class ProductRepository(CRUDBase[Products, ProductCreate, ProductUpdate]):
    """Repository for Product operations."""

    async def get_multi_with_filter(
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
    ) -> List[Products]:
        """Get products with filtering support."""
        query = select(self.model).options(
            selectinload(self.model.category),
            selectinload(self.model.supplier),
            selectinload(self.model.images)
        )

        # Build filter conditions
        conditions = []

        if name is not None:
            conditions.append(self.model.name.ilike(f"%{name}%"))

        if slug is not None:
            conditions.append(self.model.slug == slug)

        if category_id is not None:
            conditions.append(self.model.category_id == category_id)

        if supplier_id is not None:
            conditions.append(self.model.supplier_id == supplier_id)

        if is_active is not None:
            conditions.append(self.model.is_active == is_active)

        # Apply filters if any
        if conditions:
            query = query.where(and_(*conditions))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        products = result.scalars().all()

        # Load parent category type recursively for each product's category
        for product in products:
            await category_repository.load_parent_category_type_recursively(
                db, product.category
            )

        return products

    async def get_with_relationships(
        self, db: AsyncSession, product_id: int
    ) -> Optional[Products]:
        """Get product with all its relationships loaded."""
        query = select(self.model).options(
            selectinload(self.model.category),
            selectinload(self.model.supplier),
            selectinload(self.model.images)
        ).where(self.model.id == product_id)

        result = await db.execute(query)
        product = result.scalar_one_or_none()

        if product:
            await category_repository.load_parent_category_type_recursively(
                db, product.category
            )

        return product

    async def get_skus_by_product(
        self, db: AsyncSession, product_id: int, skip: int = 0, limit: int = 100
    ) -> List[Skus]:
        """Get SKUs by product."""
        query = (
            select(Skus)
            .options(
                selectinload(Skus.product).selectinload(Products.category),
                selectinload(Skus.price_details).selectinload(
                    PriceDetails.pricelist
                ),
                selectinload(Skus.sku_attribute_values).selectinload(
                    SkuAttributeValue.attribute
                )
            )
            .where(
                and_(
                    Skus.product_id == product_id,
                    Skus.is_active.is_(True)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        skus = result.scalars().all()

        # Load category type for product category
        if len(skus) > 0:
            await category_repository.load_parent_category_type_recursively(
                db, skus[0].product.category
            )

        return skus

    async def create_product(
        self, db: AsyncSession, obj_in: ProductCreate
    ) -> Products:
        """Create a new product with business validation."""

        try:
            product_data = obj_in.model_dump(
                exclude={'images'}
            )
            await self.validate_foreign_key(
                db, Categories, product_data['category_id']
            )
            await self.validate_foreign_key(
                db, Suppliers, product_data['supplier_id']
            )
            db_product = Products(**product_data)
            db.add(db_product)
            await db.commit()
            await db.refresh(db_product)

            for image_data in obj_in.images:
                image = Images(
                    object_id=db_product.id,
                    content_type='products',
                    **image_data.model_dump()
                )
                db.add(image)
            await db.commit()
            await db.refresh(db_product, ['images', 'category', 'supplier'])
            await category_repository.load_parent_category_type_recursively(
                db, db_product.category
            )
            return db_product
        except HTTPException:
            await db.rollback()
            raise
        except (ValueError, TypeError) as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create product: {str(e)}"
            )

    async def update_product(
        self,
        db: AsyncSession,
        db_obj: Products,
        obj_in: ProductUpdate
    ) -> Products:
        """Update an existing product with business validation."""

        obj_data = db_obj.__dict__
        try:
            update_data = obj_in.model_dump(
                exclude_unset=True,
                exclude={'images_to_create', 'images_to_update', 'images_to_delete'}
            )

            if update_data:
                if 'category_id' in update_data:
                    await self.validate_foreign_key(
                        db, Categories, update_data['category_id']
                    )
                if 'supplier_id' in update_data:
                    await self.validate_foreign_key(
                        db, Suppliers, update_data['supplier_id']
                    )

                for field in obj_data:
                    if field in update_data:
                        setattr(db_obj, field, update_data[field])
                db.add(db_obj)
                await db.commit()
                await db.refresh(db_obj)

            if obj_in.images_to_create:
                for image_data in obj_in.images_to_create:
                    image = Images(
                        object_id=db_obj.id,
                        content_type='products',
                        **image_data.model_dump()
                    )
                    db.add(image)

            if obj_in.images_to_update:
                for image_data in obj_in.images_to_update:
                    image = await db.get(Images, image_data.id)
                    self.check_and_validate_existing_image(
                        image, image_data.id, db_obj, "products"
                    )
                    update_data = image_data.model_dump(
                        exclude_unset=True, exclude={'id'}
                    )
                    for field, value in update_data.items():
                        setattr(image, field, value)
                    db.add(image)

            if obj_in.images_to_delete:
                for image_id in obj_in.images_to_delete:
                    image = await db.get(Images, image_id)
                    self.check_and_validate_existing_image(
                        image, image_id, db_obj, "products"
                    )
                    db.delete(image)
            await db.commit()
            await db.refresh(db_obj, ['images', 'category', 'supplier'])
            await category_repository.load_parent_category_type_recursively(
                db, db_obj.category
            )
            return db_obj
        except HTTPException:
            await db.rollback()
            raise
        except (ValueError, TypeError) as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update product: {str(e)}"
            )


# Create the repository instance
product_repository = ProductRepository(Products)
