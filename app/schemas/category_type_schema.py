from typing import Optional

from pydantic import Field

from app.schemas.base import BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema


class CategoryTypeBase(BaseSchema):
    """Base schema for CategoryType with common fields."""
    name: str = Field(..., min_length=1, max_length=100)


class CategoryTypeCreate(CategoryTypeBase, BaseCreateSchema):
    """Schema for creating a new category type.

    Used in: POST endpoints
    Contains: Only fields that client can/should provide
    """
    pass


class CategoryTypeUpdate(CategoryTypeBase, BaseUpdateSchema):
    """Schema for updating an existing category type.

    Used in: PUT/PATCH endpoints
    Contains: Optional fields that can be updated
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class CategoryTypeInDB(CategoryTypeBase, BaseInDB):
    """Schema for CategoryType as stored in database.

    Used in: Database operations, internal processing
    Contains: All database fields including auto-generated ones
    Purpose: Complete representation of database record
    """
    slug: str


class CategoryTypeResponse(CategoryTypeInDB):
    """Schema for CategoryType API responses.

    Used in: API endpoint responses (GET, POST, PUT)
    Contains: All fields that should be returned to client
    Purpose: Explicit response model for API documentation
    """
    pass
