from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.services.category_type_service import category_type_service
from app.schemas.category_type_schema import CategoryTypeResponse

router = APIRouter()


@router.get("/", response_model=List[CategoryTypeResponse])
async def get_category_types(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all category types with pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    if limit > 1000:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 1000")

    category_types = await category_type_service.get_all_category_types(
        db=db, skip=skip, limit=limit
    )
    return category_types


@router.get("/{category_type_id}", response_model=CategoryTypeResponse)
async def get_category_type(
    category_type_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific category type by ID.

    - **category_type_id**: The ID of the category type to retrieve
    """
    category_type = await category_type_service.get_category_type_by_id(
        db=db, category_type_id=category_type_id
    )
    if not category_type:
        raise HTTPException(
            status_code=404,
            detail=f"Category type with id {category_type_id} not found"
        )
    return category_type
