from typing import Optional, List, Literal
from typing_extensions import Self

from pydantic import Field, StrictStr, model_validator

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema, StrictPositiveInt
)
from app.schemas.image_schema import ImageCreate, ImageUpdate, ImageSummary


class CategoryBase(BaseSchema):
    """Base schema for Category with common fields."""
    name: StrictStr = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase, BaseCreateSchema):
    """Schema for creating a new category.

    Used in: POST endpoints
    Contains: Only fields that client can/should provide

    Business Rules:
    - Top-level categories (parent_id is None) MUST have category_type_id
    - Child categories (parent_id is not None) MUST NOT have category_type_id
    """
    category_type_id: Optional[StrictPositiveInt] = None
    parent_id: Optional[StrictPositiveInt] = None
    images: List[ImageCreate] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_category_hierarchy(self) -> Self:
        """Validate category hierarchy rules using the entire model."""
        parent_id = self.parent_id
        category_type_id = self.category_type_id

        if parent_id is None and category_type_id is None:
            raise ValueError('Top-level categories must have a category_type_id')

        if parent_id is not None and category_type_id is not None:
            raise ValueError('Child categories must not have a category_type_id')

        return self


class CategoryUpdate(CategoryBase, BaseUpdateSchema):
    """Schema for updating an existing category.

    Used in: PUT/PATCH endpoints
    Contains: Optional fields that can be updated
    """
    name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=100)
    category_type_id: Optional[StrictPositiveInt] = None
    parent_id: Optional[StrictPositiveInt] = None
    images_to_create: Optional[List[ImageCreate]] = Field(default_factory=list)
    images_to_update: Optional[List[ImageUpdate]] = Field(default_factory=list)
    images_to_delete: Optional[List[StrictPositiveInt]] = Field(default_factory=list)


class CategoryInDB(CategoryBase, BaseInDB):
    """Schema for Category as stored in database.

    Used in: Database operations, internal processing
    Contains: All database fields including auto-generated ones
    Purpose: Complete representation of database record
    """
    slug: str
    category_type_id: Optional[int] = None
    parent_id: Optional[int] = None
    children: List["CategoryInDB"] = Field(default_factory=list)


class CategoryPathItem(BaseSchema):
    """Schema for individual items in the category path."""
    name: str
    slug: str
    category_type: Optional[str] = None
    type: Literal["Category"] = "Category"


class CategoryResponse(CategoryInDB):
    """Schema for Category API responses.

    Used in: API endpoint responses (GET, POST, PUT)
    Contains: All fields that should be returned to client
    Purpose: Explicit response model for API documentation
    """
    children: List["CategoryResponse"] = Field(default_factory=list)
    full_path: List[CategoryPathItem]
    images: List[ImageSummary] = Field(default_factory=list)


# Enable forward references for self-referencing models
CategoryInDB.model_rebuild()
CategoryResponse.model_rebuild()
