from typing import Optional, List, Union, Literal, Annotated

from pydantic import Field, StrictStr

from app.schemas.base import (
    BaseSchema,
    BaseInDB,
    BaseCreateSchema,
    BaseUpdateSchema,
    StrictPositiveInt,
    PositiveDecimal,
)
from app.schemas.category_schema import CategoryPathItem
from app.schemas.product_schema import ProductPathItem


class SkuBase(BaseSchema):
    """Base schema for SKU with common fields."""
    # Use StrictStr to prevent automatic conversion from numbers
    name: StrictStr = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    product_id: StrictPositiveInt


class PriceDetailCreate(BaseSchema):
    """Schema for creating a price detail."""
    pricelist_id: StrictPositiveInt
    price: PositiveDecimal
    minimum_quantity: StrictPositiveInt


class AttributeValueInput(BaseSchema):
    """Schema for providing an attribute and its value."""
    attribute_id: StrictPositiveInt
    value: str = Field(..., min_length=1, max_length=50)


class SkuCreate(SkuBase, BaseCreateSchema):
    """Schema for creating a new SKU.

    Used in: POST endpoints
    Contains: Only fields that client can/should provide
    Note: sku_number and slug are auto-generated, not provided by client
    """
    price_details: List[PriceDetailCreate]
    attribute_values: List[AttributeValueInput]


class PriceDetailUpdate(BaseSchema):
    """Schema for updating a price detail."""
    id: StrictPositiveInt
    price: Optional[PositiveDecimal] = None
    minimum_quantity: Optional[StrictPositiveInt] = None


class SkuUpdate(SkuBase, BaseUpdateSchema):
    """Schema for updating an existing SKU.

    Used in: PUT/PATCH endpoints
    Contains: Optional fields that can be updated
    Note: sku_number and slug are not updatable
    """
    name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=100)
    product_id: Optional[StrictPositiveInt] = None
    price_details_to_create: Optional[List[PriceDetailCreate]] = None
    price_details_to_update: Optional[List[PriceDetailUpdate]] = None
    price_details_to_delete: Optional[List[StrictPositiveInt]] = None
    attribute_values: Optional[List[AttributeValueInput]] = None


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


class PricelistSummary(BaseSchema):
    """Schema for pricelist summary."""
    id: int
    name: str
    code: str

    model_config = {"from_attributes": True}


class PriceDetailSummary(BaseSchema):
    """Schema for price detail summary."""
    id: int
    price: PositiveDecimal
    minimum_quantity: int
    pricelist: PricelistSummary

    model_config = {"from_attributes": True}


class AttributeSummary(BaseSchema):
    """Schema for attribute summary."""
    id: int
    name: str
    code: str
    data_type: str
    uom: Optional[str] = None

    model_config = {"from_attributes": True}


class AttributeValueSummary(BaseSchema):
    """Schema for attribute value summary."""
    attribute: AttributeSummary
    value: str

    model_config = {"from_attributes": True}


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
    price_details: List[PriceDetailSummary]
    attribute_values: List[AttributeValueSummary] = Field(
        ..., alias='sku_attribute_values'
    )
