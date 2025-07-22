from datetime import datetime
from typing import Optional

from pydantic import BaseModel, NonNegativeInt, PositiveInt


class BaseSchema(BaseModel):
    """Base schema for common entity fields."""
    pass


class BaseCreateSchema(BaseSchema):
    """Base schema for creating entities."""
    is_active: bool = True
    sequence: NonNegativeInt = 0


class BaseUpdateSchema(BaseSchema):
    """Base schema for updating entities with optional fields."""
    is_active: Optional[bool] = None
    sequence: Optional[NonNegativeInt] = None


class BaseInDB(BaseSchema):
    """Base schema with database audit fields."""
    id: PositiveInt
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    is_active: bool
    sequence: NonNegativeInt

    model_config = {"from_attributes": True}
