from datetime import datetime
from typing import Annotated, Optional, Generic, TypeVar, List, Dict, Any

from pydantic import BaseModel, StrictBool, StrictInt, Field, AfterValidator
from decimal import Decimal, ROUND_HALF_UP

StrictNonNegativeInt = Annotated[StrictInt, Field(ge=0)]
StrictPositiveInt = Annotated[StrictInt, Field(gt=0)]
PositiveDecimal = Annotated[
    Decimal,
    AfterValidator(
        lambda x: Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    ),
    Field(..., gt=0)
]

# Generic type for response data
T = TypeVar('T')


class BaseSchema(BaseModel):
    """Base schema for common entity fields."""
    pass


class BaseCreateSchema(BaseSchema):
    """Base schema for creating entities."""
    is_active: StrictBool = True
    sequence: StrictNonNegativeInt = 0


class BaseUpdateSchema(BaseSchema):
    """Base schema for updating entities with optional fields."""
    is_active: Optional[StrictBool] = None
    sequence: Optional[StrictNonNegativeInt] = None


class BaseInDB(BaseSchema):
    """Base schema with database audit fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    is_active: bool
    sequence: int
    model_config = {"from_attributes": True}


# API Response Wrappers
class MetaSchema(BaseModel):
    """Schema for pagination metadata."""
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")


class ErrorDetailSchema(BaseModel):
    """Schema for error details."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")


class SingleItemResponse(BaseModel, Generic[T]):
    """Standard response format for single item."""
    success: bool = Field(True, description="Request successful status")
    data: Optional[T] = Field(None, description="Response data")
    error: Optional[ErrorDetailSchema] = Field(
        None, description="Error information if any"
    )


class MultipleItemsResponse(BaseModel, Generic[T]):
    """Standard response format for multiple items with pagination."""
    success: bool = Field(True, description="Request successful status")
    data: Optional[List[T]] = Field(None, description="List of response data")
    meta: Optional[MetaSchema] = Field(None, description="Pagination metadata")
    error: Optional[ErrorDetailSchema] = Field(
        None, description="Error information if any"
    )
