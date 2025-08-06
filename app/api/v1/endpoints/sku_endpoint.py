from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.services.sku_service import sku_service
from app.schemas.sku_schema import (
    SkuResponse,
    SkuCreate,
    SkuUpdate
)
from app.schemas.base import SingleItemResponse, MultipleItemsResponse
from app.utils.response_helpers import (
    create_single_item_response,
    create_multiple_items_response
)
from app.api.v1.dependencies.auth import get_current_user
from app.models.user_model import Users

router = APIRouter()


@router.get(
    "/",
    response_model=MultipleItemsResponse[SkuResponse],
    status_code=status.HTTP_200_OK
)
async def get_skus(
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
    sku_number: Optional[str] = Query(
        None, description="Filter by SKU number (exact match)"
    ),
    product_id: Optional[int] = Query(
        None, description="Filter by product ID"
    ),
    is_active: Optional[bool] = Query(
        None, description="Filter by active status"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get SKUs with optional filtering and pagination.
    This endpoint supports filtering by:
    - **name**: Partial match on SKU name
    - **slug**: Exact match on SKU slug
    - **sku_number**: Exact match on SKU number
    - **product_id**: Filter by product ID
    - **is_active**: Filter by active status

    Results are paginated using skip and limit parameters.
    Each SKU includes its full hierarchical path, price details, and attribute values.
    """
    skus, total = await sku_service.get_skus_with_filter(
        db,
        skip=skip,
        limit=limit,
        name=name,
        slug=slug,
        sku_number=sku_number,
        product_id=product_id,
        is_active=is_active
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=skus,
        page=page,
        limit=limit,
        total=total
    )


@router.post(
    "/",
    response_model=SingleItemResponse[SkuResponse],
    status_code=status.HTTP_201_CREATED
)
async def create_sku(
    sku_create: SkuCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Create a new SKU.

    This endpoint creates a SKU with:
    - Basic information (name, description, product_id)
    - Price details for different pricelists and quantity tiers
    - Attribute values with simple validation

    **Validation Rules:**
    - Product must exist and be active
    - All attributes must exist and be active
    - Attribute values must match their data types (TEXT, NUMBER, BOOLEAN, DATE)
    - SKU name must be unique within the product
    - SKU number is auto-generated (10-character hexadecimal)
    - Slug is auto-generated from name

    **Price Details:**
    - Each price detail requires pricelist_id, price, and minimum_quantity
    - Combination of (sku_id, pricelist_id, minimum_quantity) must be unique

    **Attribute Values:**
    - Simple validation: only checks if attribute exists and value matches data type
    - No complex hierarchy validation (AttributeSet is kept but not enforced)
    """
    sku = await sku_service.create_sku(
        db=db, sku_create=sku_create, created_by=current_user.id
    )
    return create_single_item_response(data=sku)


@router.get(
    "/{sku_id}",
    response_model=SingleItemResponse[SkuResponse],
    status_code=status.HTTP_200_OK
)
async def get_sku(
    sku_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific SKU by ID.

    Returns the complete SKU information including:
    - Basic SKU details (name, description, SKU number)
    - Full hierarchical path from category to SKU
    - All price details with pricelist information
    - All attribute values with attribute metadata
    """
    sku = await sku_service.get_sku_by_id(db=db, sku_id=sku_id)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU with id {sku_id} not found"
        )
    return create_single_item_response(data=sku)


@router.put(
    "/{sku_id}",
    response_model=SingleItemResponse[SkuResponse],
    status_code=status.HTTP_200_OK
)
async def update_sku(
    sku_id: int,
    sku_update: SkuUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Update an existing SKU.

    This endpoint supports partial updates of:
    - Basic SKU information (name, description, product_id)
    - Price details (create, update, delete operations)
    - Attribute values (complete replacement)

    **Price Details Management:**
    - `price_details_to_create`: List of new price details to add
    - `price_details_to_update`: List of existing price details to modify
    - `price_details_to_delete`: List of price detail IDs to remove

    **Attribute Values Management:**
    - `attribute_values`: Complete replacement of all attribute values
    - Set to empty list to remove all attributes
    - Set to null/undefined to keep existing attributes unchanged

    **Validation Rules:**
    - Same validation rules as create endpoint
    - SKU number and slug cannot be updated (auto-generated fields)
    - When updating name, uniqueness is checked within the product
    """
    sku = await sku_service.update_sku(
        db=db, sku_id=sku_id, sku_update=sku_update,
        updated_by=current_user.id,
        current_user=current_user
    )
    return create_single_item_response(data=sku)


@router.delete(
    "/{sku_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_sku(
    sku_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Delete a SKU.

    - **sku_id**: The ID of the SKU to delete

    Note: SKU cannot be deleted if it has products.
    """
    await sku_service.delete_sku(
        db=db, sku_id=sku_id, current_user=current_user
    )
