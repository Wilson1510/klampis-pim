from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.services.category_type_service import category_type_service
from app.schemas.category_type_schema import (
    CategoryTypeResponse,
    CategoryTypeCreate,
    CategoryTypeUpdate
)
from app.schemas.category_schema import CategoryResponse
from app.schemas.base import SingleItemResponse, MultipleItemsResponse
from app.utils.response_helpers import (
    create_single_item_response,
    create_multiple_items_response
)

router = APIRouter()


@router.get(
        "/",
        response_model=MultipleItemsResponse[CategoryTypeResponse],
        status_code=status.HTTP_200_OK
)
async def get_category_types(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    slug: Optional[str] = Query(None, description="Filter by slug (exact match)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get category types with optional filtering and pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **slug**: Filter by slug (exact match)
    - **is_active**: Filter by active status (true/false)
    """
    category_types, total = await category_type_service.get_category_types_with_filter(
        db=db, skip=skip, limit=limit, slug=slug, is_active=is_active
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=category_types,
        page=page,
        limit=limit,
        total=total
    )


@router.post(
    "/",
    response_model=SingleItemResponse[CategoryTypeResponse],
    status_code=status.HTTP_201_CREATED
)
async def create_category_type(
    category_type_create: CategoryTypeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new category type.

    - **name**: Name of the category type (required, max 100 chars)
    """
    category_type = await category_type_service.create_category_type(
        db=db, category_type_create=category_type_create
    )
    return create_single_item_response(data=category_type)


@router.get(
    "/{category_type_id}",
    response_model=SingleItemResponse[CategoryTypeResponse],
    status_code=status.HTTP_200_OK
)
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
    return create_single_item_response(data=category_type)


@router.put(
    "/{category_type_id}",
    response_model=SingleItemResponse[CategoryTypeResponse],
    status_code=status.HTTP_200_OK
)
async def update_category_type(
    category_type_id: int,
    category_type_update: CategoryTypeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing category type.

    - **category_type_id**: The ID of the category type to update
    - **name**: New name for the category type (optional, max 100 chars)
    """
    category_type = await category_type_service.update_category_type(
        db=db,
        category_type_id=category_type_id,
        category_type_update=category_type_update
    )
    return create_single_item_response(data=category_type)


@router.delete(
    "/{category_type_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category_type(
    category_type_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a category type.

    - **category_type_id**: The ID of the category type to delete

    Note: Category type cannot be deleted if it has associated categories.
    """
    await category_type_service.delete_category_type(
        db=db, category_type_id=category_type_id
    )


@router.get(
    "/{category_type_id}/categories/",
    response_model=MultipleItemsResponse[CategoryResponse],
    status_code=status.HTTP_200_OK
)
async def get_categories_by_type(
    category_type_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all categories under a specific category type.

    - **category_type_id**: The ID of the category type
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    categories, total = await category_type_service.get_categories_by_type(
        db=db,
        category_type_id=category_type_id,
        skip=skip,
        limit=limit
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=categories,
        page=page,
        limit=limit,
        total=total
    )
