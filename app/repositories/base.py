from typing import Any, Dict, Generic, List, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from app.core.base import Base
from fastapi import HTTPException, status

# Definisikan tipe generik untuk model dan skema
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Kelas CRUD generik dengan metode default untuk:
        - Create, Read, Update, Delete (CRUD).

        **Parameter**
        * `model`: Sebuah model SQLAlchemy
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        result = await db.get(self.model, id)
        return result

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
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
                detail=f"Internal server error: {e}"
            )

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # exclude_unset=True agar hanya field yang dikirim yang di-update
            update_data = obj_in.model_dump(exclude_unset=True)

        if not update_data:
            return db_obj

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
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
                detail=f"Internal server error: {e}"
            )

    async def soft_delete(self, db: AsyncSession, id: int) -> ModelType | None:
        """Soft delete an object by setting is_active to False."""
        obj = await self.get(db, id=id)
        if obj:
            query = (
                update(self.model)
                .where(self.model.id == id)
                .values(is_active=False)
            )
            await db.execute(query)
            await db.commit()
            await db.refresh(obj)
            return obj
        return None

    async def hard_delete(self, db: AsyncSession, *, id: int) -> ModelType | None:
        """Hard delete an object by deleting it from the database."""
        obj = await db.get(self.model, id)
        if obj:
            db.delete(obj)
            await db.commit()
        return obj

    async def get_by_field(
        self, db: AsyncSession, field_name: str, field_value: Any
    ) -> ModelType | None:
        """
        Generic method to get a single record by any field.

        Args:
            db: Database session
            field_name: Name of the field to filter by (e.g., 'name', 'email', 'slug')
            field_value: Value to match

        Returns:
            Model instance or None if not found

        Example:
            supplier = await repository.get_by_field(db, 'email', 'test@example.com')
            category = await repository.get_by_field(db, 'name', 'Electronics')
        """
        # Validate that the field exists on the model
        if not hasattr(self.model, field_name):
            raise ValueError(
                f"Field '{field_name}' does not exist on model {self.model.__name__}"
            )

        field_attr = getattr(self.model, field_name)
        query = select(self.model).where(field_attr == field_value)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def validate_foreign_key(
        self,
        db: AsyncSession,
        foreign_model: ModelType,
        foreign_key_value: int
    ):
        # Use generic field lookup
        query = select(foreign_model).where(and_(
                foreign_model.id == foreign_key_value,
                foreign_model.is_active.is_(True)
            ))
        result = await db.execute(query)
        foreign_obj = result.scalar_one_or_none()

        if not foreign_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"{foreign_model.__name__} with id {foreign_key_value} not found"
                )
            )
