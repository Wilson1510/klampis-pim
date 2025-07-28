from typing import Optional

from pydantic import Field, StrictStr

from app.schemas.base import BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema


class PricelistBase(BaseSchema):
    """Base schema for Pricelist with common fields."""
    # Use StrictStr to prevent automatic conversion from numbers
    name: StrictStr = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class PricelistCreate(PricelistBase, BaseCreateSchema):
    """Schema for creating a new pricelist.

    Used in: POST endpoints
    Contains: Only fields that client can/should provide
    Note: code is auto-generated from name, not provided by client
    """
    pass


class PricelistUpdate(PricelistBase, BaseUpdateSchema):
    """Schema for updating an existing pricelist.

    Used in: PUT/PATCH endpoints
    Contains: Optional fields that can be updated
    Note: code is not updatable as it's auto-generated from name
    """
    name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=50)


class PricelistInDB(PricelistBase, BaseInDB):
    """Schema for Pricelist as stored in database.

    Used in: Database operations, internal processing
    Contains: All database fields including auto-generated ones
    Purpose: Complete representation of database record
    """
    code: str


class PricelistResponse(PricelistInDB):
    """Schema for Pricelist API responses.

    Used in: API endpoint responses (GET, POST, PUT)
    Contains: All fields that should be returned to client
    Purpose: Explicit response model for API documentation
    """
    pass
