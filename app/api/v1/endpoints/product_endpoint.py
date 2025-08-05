from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.services.product_service import product_service
from app.schemas.product_schema import (
    ProductResponse,
    ProductCreate,
    ProductUpdate
)
from app.schemas.sku_schema import SkuResponse
from app.schemas.base import SingleItemResponse, MultipleItemsResponse
from app.utils.response_helpers import (
    create_single_item_response,
    create_multiple_items_response
)
from app.api.v1.dependencies.auth import get_current_user
from app.models import Users

router = APIRouter()


@router.get(
    "/",
    response_model=MultipleItemsResponse[ProductResponse],
    status_code=status.HTTP_200_OK
)
async def get_products(
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
    category_id: Optional[int] = Query(
        None, description="Filter by category ID"
    ),
    supplier_id: Optional[int] = Query(
        None, description="Filter by supplier ID"
    ),
    is_active: Optional[bool] = Query(
        None, description="Filter by active status"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get products with optional filtering and pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **name**: Filter by name (partial match)
    - **slug**: Filter by slug (exact match)
    - **category_id**: Filter by category ID
    - **supplier_id**: Filter by supplier ID
    - **is_active**: Filter by active status (true/false)
    """

    products, total = await product_service.get_products_with_filter(
        db=db,
        skip=skip,
        limit=limit,
        name=name,
        slug=slug,
        category_id=category_id,
        supplier_id=supplier_id,
        is_active=is_active
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=products,
        page=page,
        limit=limit,
        total=total
    )


@router.post(
    "/",
    response_model=SingleItemResponse[ProductResponse],
    status_code=status.HTTP_201_CREATED
)
async def create_product(
    product_create: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Create a new product.

    **Requires authentication** (enforced at router level).
    All authenticated users can create products.

    - **name**: Name of the product (required, max 100 chars)
    - **description**: Optional description
    - **category_id**: Required category ID
    - **supplier_id**: Required supplier ID
    - **images**: Optional list of images to associate with the product

    Business Rules:
    - Product name must be unique
    - Category and supplier must exist
    - Created by current authenticated user
    """
    product = await product_service.create_product(
        db=db, product_create=product_create, created_by=current_user.id
    )
    return create_single_item_response(data=product)


@router.get(
    "/{product_id}",
    response_model=SingleItemResponse[ProductResponse],
    status_code=status.HTTP_200_OK
)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific product by ID.

    - **product_id**: The ID of the product to retrieve
    """
    product = await product_service.get_product_by_id(
        db=db, product_id=product_id
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return create_single_item_response(data=product)


@router.put(
    "/{product_id}",
    response_model=SingleItemResponse[ProductResponse],
    status_code=status.HTTP_200_OK
)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Update an existing product.

    **Access Control:**
    - ADMIN, MANAGER, SYSTEM: Can update any product
    - USER: Can only update products they created

    - **product_id**: The ID of the product to update
    - **name**: New name for the product (optional, max 100 chars)
    - **description**: New description (optional)
    - **category_id**: New category ID (optional)
    - **supplier_id**: New supplier ID (optional)
    - **images_to_create**: List of new images to add (optional)
    - **images_to_update**: List of existing images to update (optional)
    - **images_to_delete**: List of image IDs to delete (optional)

    Business Rules:
    - Product name must be unique if updated
    - Category and supplier must exist if updated
    - Authorization check handled by service layer
    """
    product = await product_service.update_product(
        db=db,
        product_id=product_id,
        product_update=product_update,
        updated_by=current_user.id,
        current_user=current_user
    )
    return create_single_item_response(data=product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Delete a product.

    - **product_id**: The ID of the product to delete

    Note: Product cannot be deleted if it has SKUs.
    """
    await product_service.delete_product(
        db=db, product_id=product_id, current_user=current_user
    )


@router.get(
    "/{product_id}/skus/",
    response_model=MultipleItemsResponse[SkuResponse],
    status_code=status.HTTP_200_OK
)
async def get_product_skus(
    product_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all SKUs of a specific product.

    - **product_id**: The ID of the product
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    skus, total = await product_service.get_skus_by_product(
        db=db,
        product_id=product_id,
        skip=skip,
        limit=limit
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=skus,
        page=page,
        limit=limit,
        total=total
    )
