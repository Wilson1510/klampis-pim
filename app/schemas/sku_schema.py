from typing import Optional, List, Union, Literal, Annotated

from pydantic import Field, StrictStr

from app.schemas.base import (
    BaseSchema,
    BaseInDB,
    BaseCreateSchema,
    BaseUpdateSchema,
    StrictPositiveInt,
)
from app.schemas.category_schema import CategoryPathItem
from app.schemas.product_schema import ProductPathItem


class SkuBase(BaseSchema):
    """Base schema for SKU with common fields."""
    # Use StrictStr to prevent automatic conversion from numbers
    name: StrictStr = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    product_id: StrictPositiveInt


class SkuCreate(SkuBase, BaseCreateSchema):
    """Schema for creating a new SKU.

    Used in: POST endpoints
    Contains: Only fields that client can/should provide
    Note: sku_number and slug are auto-generated, not provided by client
    """
    pass


class SkuUpdate(SkuBase, BaseUpdateSchema):
    """Schema for updating an existing SKU.

    Used in: PUT/PATCH endpoints
    Contains: Optional fields that can be updated
    Note: sku_number and slug are not updatable
    """
    name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=100)
    product_id: Optional[StrictPositiveInt] = None


class SkuInDB(SkuBase, BaseInDB):
    """Schema for SKU as stored in database.

    Used in: Database operations, internal processing
    Contains: All database fields including auto-generated ones
    Purpose: Complete representation of database record
    """
    slug: str
    sku_number: str


class SkuPathItem(BaseSchema):
    """Schema for SKU items in the path."""
    name: str
    slug: str
    sku_number: str
    type: Literal["SKU"] = "SKU"


class SkuResponse(SkuInDB):
    """Schema for SKU API responses.

    Used in: API endpoint responses (GET, POST, PUT)
    Contains: All fields that should be returned to client
    Purpose: Explicit response model for API documentation
    """
    full_path: List[
        Annotated[
            Union[CategoryPathItem, ProductPathItem, SkuPathItem],
            Field(discriminator='type')
        ]
    ]
