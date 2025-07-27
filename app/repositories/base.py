from typing import Any, Dict, Generic, List, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
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
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
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
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
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
