from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_db
from app.services.attribute_service import attribute_service
from app.schemas.attribute_schema import (
    AttributeResponse,
    AttributeCreate,
    AttributeUpdate
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
        response_model=MultipleItemsResponse[AttributeResponse],
        status_code=status.HTTP_200_OK
)
async def get_attributes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    code: Optional[str] = Query(None, description="Filter by code (partial match)"),
    data_type: Optional[str] = Query(
        None, description="Filter by data type (TEXT, NUMBER, BOOLEAN, DATE)"
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get attributes with optional filtering and pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **name**: Filter by name (partial match)
    - **code**: Filter by code (partial match)
    - **data_type**: Filter by data type (TEXT, NUMBER, BOOLEAN, DATE)
    - **is_active**: Filter by active status (true/false)
    """
    attributes, total = await attribute_service.get_attributes_with_filter(
        db=db,
        skip=skip,
        limit=limit,
        name=name,
        code=code,
        data_type=data_type,
        is_active=is_active
    )

    # Calculate page number (1-based)
    page = (skip // limit) + 1

    return create_multiple_items_response(
        data=attributes,
        page=page,
        limit=limit,
        total=total
    )


@router.post(
    "/",
    response_model=SingleItemResponse[AttributeResponse],
    status_code=status.HTTP_201_CREATED
)
async def create_attribute(
    attribute_create: AttributeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Create a new attribute.

    - **name**: Name of the attribute (required, max 50 chars)
    - **data_type**: Data type (TEXT, NUMBER, BOOLEAN, DATE) (default: TEXT)
    - **uom**: Unit of measure (optional, max 15 chars)
    """
    attribute = await attribute_service.create_attribute(
        db=db, attribute_create=attribute_create, created_by=current_user.id
    )
    return create_single_item_response(data=attribute)


@router.get(
    "/{attribute_id}",
    response_model=SingleItemResponse[AttributeResponse],
    status_code=status.HTTP_200_OK
)
async def get_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific attribute by ID.

    - **attribute_id**: The ID of the attribute to retrieve
    """
    attribute = await attribute_service.get_attribute_by_id(
        db=db, attribute_id=attribute_id
    )
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attribute with id {attribute_id} not found"
        )
    return create_single_item_response(data=attribute)


@router.put(
    "/{attribute_id}",
    response_model=SingleItemResponse[AttributeResponse],
    status_code=status.HTTP_200_OK
)
async def update_attribute(
    attribute_id: int,
    attribute_update: AttributeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Update an existing attribute.

    - **attribute_id**: The ID of the attribute to update
    - **name**: New name for the attribute (optional, max 50 chars)
    - **data_type**: New data type (optional)
    - **uom**: New unit of measure (optional, max 15 chars)
    """
    attribute = await attribute_service.update_attribute(
        db=db,
        attribute_id=attribute_id,
        attribute_update=attribute_update,
        updated_by=current_user.id,
        current_user=current_user
    )
    return create_single_item_response(data=attribute)


@router.delete(
    "/{attribute_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Delete an attribute.

    - **attribute_id**: The ID of the attribute to delete

    Note: Attribute cannot be deleted if it has associated SKU attribute values.
    """
    await attribute_service.delete_attribute(
        db=db, attribute_id=attribute_id, current_user=current_user
    )
