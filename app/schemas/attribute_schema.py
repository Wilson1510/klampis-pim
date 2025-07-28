from typing import Optional, Literal

from pydantic import Field, StrictStr

from app.schemas.base import (
    BaseSchema,
    BaseInDB,
    BaseCreateSchema,
    BaseUpdateSchema,
)


class AttributeBase(BaseSchema):
    """Base schema for Attribute with common fields."""
    # Use StrictStr to prevent automatic conversion from numbers
    name: StrictStr = Field(..., min_length=1, max_length=50)
    data_type: Literal["TEXT", "NUMBER", "BOOLEAN", "DATE"] = Field(default="TEXT")
    uom: Optional[StrictStr] = Field(default=None, max_length=15)


class AttributeCreate(AttributeBase, BaseCreateSchema):
    """Schema for creating a new attribute.

    Used in: POST endpoints
    Contains: Only fields that client can/should provide
    Note: Auto-generated fields are handled by the model
    """
    pass


class AttributeUpdate(AttributeBase, BaseUpdateSchema):
    """Schema for updating an existing attribute.

    Used in: PUT/PATCH endpoints
    Contains: Optional fields that can be updated
    """
    name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=50)
    data_type: Optional[Literal["TEXT", "NUMBER", "BOOLEAN", "DATE"]] = None
    uom: Optional[StrictStr] = Field(default=None, max_length=15)


class AttributeInDB(AttributeBase, BaseInDB):
    """Schema for Attribute as stored in database.

    Used in: Database operations, internal processing
    Contains: All database fields including auto-generated ones
    Purpose: Complete representation of database record
    """
    code: str


class AttributeResponse(AttributeInDB):
    """Schema for Attribute API responses.

    Used in: API endpoint responses (GET, POST, PUT)
    Contains: All fields that should be returned to client
    Purpose: Explicit response model for API documentation
    """
    pass
