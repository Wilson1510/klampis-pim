from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.services.supplier_service import supplier_service
from app.schemas.supplier_schema import (
    SupplierResponse,
    SupplierCreate,
    SupplierUpdate
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
    response_model=MultipleItemsResponse[SupplierResponse],
    status_code=status.HTTP_200_OK
)
async def get_suppliers(
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
    company_type: Optional[str] = Query(
        None, description="Filter by company type"
    ),
    email: Optional[str] = Query(
        None, description="Filter by email (partial match)"
    ),
    contact: Optional[str] = Query(
        None, description="Filter by contact (partial match)"
    ),
    is_active: Optional[bool] = Query(
        None, description="Filter by active status"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get suppliers with optional filtering and pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **name**: Filter by name (partial match)
    - **slug**: Filter by slug (exact match)
    - **company_type**: Filter by company type (INDIVIDUAL, PT, CV, UD)
    - **email**: Filter by email (partial match)
    - **contact**: Filter by contact (partial match)
    - **is_active**: Filter by active status (true/false)
    """

    suppliers, total = await supplier_service.get_suppliers_with_filter(
        db=db,
        skip=skip,
        limit=limit,
        name=name,
        slug=slug,
        company_type=company_type,
        email=email,
        contact=contact,
        is_active=is_active
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=suppliers,
        page=page,
        limit=limit,
        total=total
    )


@router.post(
    "/",
    response_model=SingleItemResponse[SupplierResponse],
    status_code=status.HTTP_201_CREATED
)
async def create_supplier(
    supplier_create: SupplierCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new supplier.

    - **name**: Name of the supplier (required, max 100 chars)
    - **company_type**: Type of company (INDIVIDUAL, PT, CV, UD)
    - **address**: Optional address
    - **contact**: Contact number (required, 10-13 digits)
    - **email**: Email address (required, max 50 chars)

    Business Rules:
    - Name must be unique
    - Email must be unique
    - Contact must be unique and contain only digits
    """
    supplier = await supplier_service.create_supplier(
        db=db, supplier_create=supplier_create
    )
    return create_single_item_response(data=supplier)


@router.get(
    "/{supplier_id}",
    response_model=SingleItemResponse[SupplierResponse],
    status_code=status.HTTP_200_OK
)
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific supplier by ID.

    - **supplier_id**: The ID of the supplier to retrieve
    """
    supplier = await supplier_service.get_supplier_by_id(
        db=db, supplier_id=supplier_id
    )
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id {supplier_id} not found"
        )
    return create_single_item_response(data=supplier)


@router.put(
    "/{supplier_id}",
    response_model=SingleItemResponse[SupplierResponse],
    status_code=status.HTTP_200_OK
)
async def update_supplier(
    supplier_id: int,
    supplier_update: SupplierUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing supplier.

    - **supplier_id**: The ID of the supplier to update
    - **name**: New name for the supplier (optional, max 100 chars)
    - **company_type**: New company type (optional)
    - **address**: New address (optional)
    - **contact**: New contact number (optional, 10-13 digits)
    - **email**: New email address (optional, max 50 chars)

    Business Rules:
    - Name must be unique if changed
    - Email must be unique if changed
    - Contact must be unique and contain only digits if changed
    """
    supplier = await supplier_service.update_supplier(
        db=db,
        supplier_id=supplier_id,
        supplier_update=supplier_update
    )
    return create_single_item_response(data=supplier)


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a supplier.

    - **supplier_id**: The ID of the supplier to delete

    Note: Supplier cannot be deleted if it has products.
    """
    await supplier_service.delete_supplier(db=db, supplier_id=supplier_id)


@router.get(
    "/{supplier_id}/products/",
    response_model=MultipleItemsResponse[ProductResponse],
    status_code=status.HTTP_200_OK
)
async def get_supplier_products(
    supplier_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all products from a specific supplier.

    - **supplier_id**: The ID of the supplier
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    products, total = await supplier_service.get_products_by_supplier(
        db=db,
        supplier_id=supplier_id,
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
