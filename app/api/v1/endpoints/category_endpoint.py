from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.services.category_service import category_service
from app.schemas.category_schema import (
    CategoryResponse,
    CategoryCreate,
    CategoryUpdate
)
from app.schemas.product_schema import ProductResponse
from app.schemas.base import SingleItemResponse, MultipleItemsResponse
from app.utils.response_helpers import (
    create_single_item_response,
    create_multiple_items_response
)

router = APIRouter()


@router.get(
    "/",
    response_model=MultipleItemsResponse[CategoryResponse],
    status_code=status.HTTP_200_OK
)
async def get_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    name: Optional[str] = Query(
        None, description="Filter by name (partial match)"
    ),
    slug: Optional[str] = Query(
        None, description="Filter by slug (exact match)"
    ),
    category_type_id: Optional[int] = Query(
        None, description="Filter by category type ID"
    ),
    parent_id: Optional[int] = Query(
        None, description="Filter by parent ID"
    ),
    is_active: Optional[bool] = Query(
        None, description="Filter by active status"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get categories with optional filtering and pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **name**: Filter by name (partial match)
    - **slug**: Filter by slug (exact match)
    - **category_type_id**: Filter by category type ID
    - **parent_id**: Filter by parent ID
    - **is_active**: Filter by active status (true/false)
    """

    categories, total = await category_service.get_categories_with_filter(
        db=db,
        skip=skip,
        limit=limit,
        name=name,
        slug=slug,
        category_type_id=category_type_id,
        parent_id=parent_id,
        is_active=is_active
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=categories,
        page=page,
        limit=limit,
        total=total
    )


@router.post(
    "/",
    response_model=SingleItemResponse[CategoryResponse],
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_create: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new category.

    - **name**: Name of the category (required, max 100 chars)
    - **description**: Optional description
    - **category_type_id**: Required for top-level categories, null for children
    - **parent_id**: Required for child categories, null for top-level
    - **images**: Optional list of images to associate with the category

    Business Rules:
    - Top-level categories (parent_id is null) MUST have category_type_id
    - Child categories (parent_id is not null) MUST NOT have category_type_id
    """
    category = await category_service.create_category(
        db=db, category_create=category_create
    )
    return create_single_item_response(data=category)


@router.get(
    "/{category_id}",
    response_model=SingleItemResponse[CategoryResponse],
    status_code=status.HTTP_200_OK
)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific category by ID.

    - **category_id**: The ID of the category to retrieve
    """
    category = await category_service.get_category_by_id(
        db=db, category_id=category_id
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    return create_single_item_response(data=category)


@router.put(
    "/{category_id}",
    response_model=SingleItemResponse[CategoryResponse],
    status_code=status.HTTP_200_OK
)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing category.

    - **category_id**: The ID of the category to update
    - **name**: New name for the category (optional, max 100 chars)
    - **description**: New description (optional)
    - **category_type_id**: New category type ID (optional)
    - **parent_id**: New parent ID (optional)
    - **images_to_create**: List of new images to add (optional)
    - **images_to_update**: List of existing images to update (optional)
    - **images_to_delete**: List of image IDs to delete (optional)

    Business Rules:
    - Top-level categories (parent_id is null) MUST have category_type_id
    - Child categories (parent_id is not null) MUST NOT have category_type_id
    """
    category = await category_service.update_category(
        db=db,
        category_id=category_id,
        category_update=category_update
    )
    return create_single_item_response(data=category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a category.

    - **category_id**: The ID of the category to delete

    Note: Category cannot be deleted if it has child categories or products.
    """
    await category_service.delete_category(db=db, category_id=category_id)


@router.get(
    "/{category_id}/children/",
    response_model=MultipleItemsResponse[CategoryResponse],
    status_code=status.HTTP_200_OK
)
async def get_category_children(
    category_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all direct children of a specific category.

    - **category_id**: The ID of the parent category
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    children, total = await category_service.get_children_by_parent(
        db=db,
        parent_id=category_id,
        skip=skip,
        limit=limit
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=children,
        page=page,
        limit=limit,
        total=total
    )


@router.get(
    "/{category_id}/products/",
    response_model=MultipleItemsResponse[ProductResponse],
    status_code=status.HTTP_200_OK
)
async def get_category_products(
    category_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all products of a specific category.

    - **category_id**: The ID of the category
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    products, total = await category_service.get_products_by_category(
        db=db,
        category_id=category_id,
        skip=skip,
        limit=limit
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=products,
        page=page,
        limit=limit,
        total=total
    )
