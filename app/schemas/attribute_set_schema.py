from typing import Optional, List, Literal

from pydantic import Field, StrictStr

from app.schemas.base import (
    BaseSchema,
    BaseInDB,
    BaseCreateSchema,
    BaseUpdateSchema,
    StrictPositiveInt,
)


class AttributeSetBase(BaseSchema):
    """Base schema for AttributeSet with common fields."""
    name: StrictStr = Field(..., min_length=1, max_length=100)


class AttributeSetCreate(AttributeSetBase, BaseCreateSchema):
    """Schema for creating a new attribute set."""
    category_id: StrictPositiveInt
    attribute_ids: List[StrictPositiveInt]


class AttributeSetUpdate(AttributeSetBase, BaseUpdateSchema):
    """Schema for updating an existing attribute set."""
    name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=100)
    attribute_ids: List[StrictPositiveInt] = Field(default_factory=list)


class AttributeSummary(BaseSchema):
    """Schema for attribute summary."""
    id: int
    name: str
    code: str
    data_type: Literal["TEXT", "NUMBER", "BOOLEAN", "DATE"]
    uom: Optional[str] = None

    model_config = {"from_attributes": True}


class CategorySummary(BaseSchema):
    """Schema for category summary."""
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class AttributeSetInDB(AttributeSetBase, BaseInDB):
    """Schema for AttributeSet as stored in database."""
    slug: str
    categories: List[CategorySummary]
    attributes: List[AttributeSummary]


class AttributeSetResponse(AttributeSetInDB):
    """Schema for AttributeSet API responses."""
    pass
