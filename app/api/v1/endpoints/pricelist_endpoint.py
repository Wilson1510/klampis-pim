from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.services.pricelist_service import pricelist_service
from app.schemas.pricelist_schema import (
    PricelistResponse,
    PricelistCreate,
    PricelistUpdate
)
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
        response_model=MultipleItemsResponse[PricelistResponse],
        status_code=status.HTTP_200_OK
)
async def get_pricelists(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    code: Optional[str] = Query(None, description="Filter by code (partial match)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pricelists with optional filtering and pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **name**: Filter by name (partial match)
    - **code**: Filter by code (partial match)
    - **is_active**: Filter by active status (true/false)
    """
    pricelists, total = await pricelist_service.get_pricelists_with_filter(
        db=db,
        skip=skip,
        limit=limit,
        name=name,
        code=code,
        is_active=is_active
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=pricelists,
        page=page,
        limit=limit,
        total=total
    )


@router.post(
    "/",
    response_model=SingleItemResponse[PricelistResponse],
    status_code=status.HTTP_201_CREATED
)
async def create_pricelist(
    pricelist_create: PricelistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Create a new pricelist.

    - **name**: Name of the pricelist (required, max 50 chars)
    - **description**: Description of the pricelist (optional)
    """
    pricelist = await pricelist_service.create_pricelist(
        db=db, pricelist_create=pricelist_create, created_by=current_user.id
    )
    return create_single_item_response(data=pricelist)


@router.get(
    "/{pricelist_id}",
    response_model=SingleItemResponse[PricelistResponse],
    status_code=status.HTTP_200_OK
)
async def get_pricelist(
    pricelist_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific pricelist by ID.

    - **pricelist_id**: The ID of the pricelist to retrieve
    """
    pricelist = await pricelist_service.get_pricelist_by_id(
        db=db, pricelist_id=pricelist_id
    )
    if not pricelist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pricelist with id {pricelist_id} not found"
        )
    return create_single_item_response(data=pricelist)


@router.put(
    "/{pricelist_id}",
    response_model=SingleItemResponse[PricelistResponse],
    status_code=status.HTTP_200_OK
)
async def update_pricelist(
    pricelist_id: int,
    pricelist_update: PricelistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Update an existing pricelist.

    - **pricelist_id**: The ID of the pricelist to update
    - **name**: New name for the pricelist (optional, max 50 chars)
    - **description**: New description for the pricelist (optional)
    """
    pricelist = await pricelist_service.update_pricelist(
        db=db,
        pricelist_id=pricelist_id,
        pricelist_update=pricelist_update,
        updated_by=current_user.id,
        current_user=current_user
    )
    return create_single_item_response(data=pricelist)


@router.delete(
    "/{pricelist_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_pricelist(
    pricelist_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Delete a pricelist.

    - **pricelist_id**: The ID of the pricelist to delete

    Note: Pricelist cannot be deleted if it has associated price details.
    """
    await pricelist_service.delete_pricelist(
        db=db, pricelist_id=pricelist_id, current_user=current_user
    )
