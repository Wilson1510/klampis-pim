from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import Categories, Images, Products, CategoryTypes
from app.schemas.category_schema import CategoryCreate, CategoryUpdate
from app.repositories.base import CRUDBase


class CategoryRepository(
    CRUDBase[Categories, CategoryCreate, CategoryUpdate]
):
    """Repository for Category operations."""

    async def get_multi_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        category_type_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[Categories]:
        """Get categories with filtering support."""
        query = select(self.model).options(
            selectinload(self.model.category_type),
            selectinload(self.model.parent),
            selectinload(self.model.images)
        )

        # Build filter conditions
        conditions = []

        if name is not None:
            conditions.append(self.model.name.ilike(f"%{name}%"))

        if slug is not None:
            conditions.append(self.model.slug == slug)

        if category_type_id is not None:
            conditions.append(self.model.category_type_id == category_type_id)

        if parent_id is not None:
            conditions.append(self.model.parent_id == parent_id)

        if is_active is not None:
            conditions.append(self.model.is_active == is_active)

        # Apply filters if any
        if conditions:
            query = query.where(and_(*conditions))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        categories = result.scalars().all()

        # Load children recursively for each category
        for category in categories:
            await self.load_children_recursively(db, category)
            if category.parent is not None:
                await self.load_parent_category_type_recursively(db, category.parent)

        return categories

    async def get_children_by_parent(
        self,
        db: AsyncSession,
        parent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Categories]:
        """Get all direct children of a category."""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.parent),
                selectinload(self.model.images)
            )
            .where(self.model.parent_id == parent_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        categories = result.scalars().all()

        # Load children recursively for each category
        for category in categories:
            await self.load_children_recursively(db, category)
            await self.load_parent_category_type_recursively(db, category)

        return categories

    async def get_products_by_category(
        self, db: AsyncSession, category_id: int, skip: int = 0, limit: int = 100
    ) -> List[Products]:
        """Get products by category."""
        query = (
            select(Products)
            .options(
                selectinload(Products.category),
                selectinload(Products.images)
            )
            .where(Products.category_id == category_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        products = result.scalars().all()
        if len(products) > 0:
            await self.load_parent_category_type_recursively(db, products[0].category)
        return products

    async def create_category(
        self, db: AsyncSession, obj_in: CategoryCreate, created_by: int
    ) -> Categories:
        """Create a new category."""
        try:
            category_data = obj_in.model_dump(
                exclude={'images'}
            )
            category_data['created_by'] = created_by
            category_data['updated_by'] = created_by
            if category_data['parent_id']:
                await self.validate_foreign_key(
                    db, Categories, category_data['parent_id']
                )
            if category_data['category_type_id']:
                await self.validate_foreign_key(
                    db, CategoryTypes, category_data['category_type_id']
                )
            db_category = Categories(**category_data)
            db.add(db_category)
            await db.commit()
            await db.refresh(db_category)

            for image_data in obj_in.images:
                image = Images(
                    object_id=db_category.id,
                    content_type="categories",
                    **image_data.model_dump()
                )
                db.add(image)

            await db.commit()
            await self.load_children_recursively(db, db_category)
            await db.refresh(db_category, ['images'])
            await self.load_parent_category_type_recursively(db, db_category)
            return db_category
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
                detail=f"Failed to create category: {str(e)}"
            )

    async def update_category(
        self, db: AsyncSession, db_obj: Categories, obj_in: CategoryUpdate,
        updated_by: int
    ) -> Categories:
        """Update an existing category."""
        obj_data = db_obj.__dict__
        try:
            update_data = obj_in.model_dump(
                exclude_unset=True,
                exclude={'images_to_create', 'images_to_update', 'images_to_delete'}
            )
            update_data['updated_by'] = updated_by

            if update_data:
                if 'parent_id' in update_data:
                    await self.validate_foreign_key(
                        db, Categories, update_data['parent_id']
                    )

                if 'category_type_id' in update_data:
                    await self.validate_foreign_key(
                        db, CategoryTypes, update_data['category_type_id']
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
                        content_type="categories",
                        **image_data.model_dump()
                    )
                    db.add(image)

            if obj_in.images_to_update:
                for image_data in obj_in.images_to_update:
                    image = await db.get(Images, image_data.id)
                    self.check_and_validate_existing_image(
                        image, image_data.id, db_obj, "categories"
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
                        image, image_id, db_obj, "categories"
                    )
                    await db.delete(image)
            await db.commit()
            await self.load_children_recursively(db, db_obj)
            await db.refresh(db_obj, ['images'])
            await self.load_parent_category_type_recursively(db, db_obj)
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
                detail=f"Failed to update category: {str(e)}"
            )

    async def get_with_full_relations(
        self, db: AsyncSession, category_id: int
    ) -> Categories | None:
        """Get category with all relations loaded."""
        query = select(self.model).options(
            selectinload(self.model.category_type),
            selectinload(self.model.parent),
            selectinload(self.model.images)
        ).where(self.model.id == category_id)

        result = await db.execute(query)
        category = result.scalar_one_or_none()

        if category:
            await self.load_children_recursively(db, category)
            await self.load_parent_category_type_recursively(db, category)

        return category

    async def load_parent_category_type_recursively(
        self, session: AsyncSession, category: Categories
    ) -> None:
        """
        Load parent category type recursively. This will be used mostly for
        getting the category type of the parent category to be used for full path.
        """
        stmt = select(Categories).where(Categories.id == category.id).options(
            selectinload(Categories.category_type),
            selectinload(Categories.parent)
        )
        result = await session.execute(stmt)
        data = result.scalar_one_or_none()
        if data.parent is not None:
            await self.load_parent_category_type_recursively(session, data.parent)

    async def load_children_recursively(
        self, session: AsyncSession, category: Categories
    ) -> None:
        """
        Load all children recursively.
        Warning: This will cause N+1 query problem.
        """
        await session.refresh(category, ['children'])
        for child in category.children:
            await self.load_children_recursively(session, child)


# Create instance to be used as dependency
category_repository = CategoryRepository(Categories)
