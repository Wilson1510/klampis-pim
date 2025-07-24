from typing import Optional, List, Self

from pydantic import Field, StrictStr, model_validator

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema, StrictPositiveInt
)


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


class CategoryTypeSchema(BaseSchema):
    """Nested schema for category type information."""
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class CategoryInDB(CategoryBase, BaseInDB):
    """Schema for Category as stored in database.

    Used in: Database operations, internal processing
    Contains: All database fields including auto-generated ones
    Purpose: Complete representation of database record
    """
    slug: str
    category_type_id: Optional[int] = None
    parent_id: Optional[int] = None
    children: List["CategoryInDB"] = []


class CategoryResponse(CategoryInDB):
    """Schema for Category API responses.

    Used in: API endpoint responses (GET, POST, PUT)
    Contains: All fields that should be returned to client
    Purpose: Explicit response model for API documentation
    """
    pass


# Enable forward references for self-referencing models
CategoryResponse.model_rebuild()
