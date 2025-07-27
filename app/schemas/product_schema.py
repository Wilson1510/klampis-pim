from typing import Optional, List, Union

from pydantic import Field, StrictStr

from app.schemas.base import (
    BaseSchema,
    BaseInDB,
    BaseCreateSchema,
    BaseUpdateSchema,
    StrictPositiveInt,
)
from app.schemas.category_schema import CategoryPathItem


class ProductBase(BaseSchema):
    """Base schema for Product with common fields."""
    # Use StrictStr to prevent automatic conversion from numbers
    name: StrictStr = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category_id: StrictPositiveInt
    supplier_id: StrictPositiveInt


class ProductCreate(ProductBase, BaseCreateSchema):
    """Schema for creating a new product.

    Used in: POST endpoints
    Contains: Only fields that client can/should provide
    """
    pass


class ProductUpdate(ProductBase, BaseUpdateSchema):
    """Schema for updating an existing product.

    Used in: PUT/PATCH endpoints
    Contains: Optional fields that can be updated
    """
    name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=100)
    category_id: Optional[StrictPositiveInt] = None
    supplier_id: Optional[StrictPositiveInt] = None


class ProductInDB(ProductBase, BaseInDB):
    """Schema for Product as stored in database.

    Used in: Database operations, internal processing
    Contains: All database fields including auto-generated ones
    Purpose: Complete representation of database record
    """
    slug: str


class ProductPathItem(BaseSchema):
    """Schema for product items in the product path."""
    name: str
    slug: str
    type: str = "Product"


class ProductResponse(ProductInDB):
    """Schema for Product API responses.

    Used in: API endpoint responses (GET, POST, PUT)
    Contains: All fields that should be returned to client
    Purpose: Explicit response model for API documentation
    """
    full_path: List[Union[CategoryPathItem, ProductPathItem]]
