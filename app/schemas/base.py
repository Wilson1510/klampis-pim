from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema for common entity fields."""
    pass


class BaseCreateSchema(BaseSchema):
    """Base schema for creating entities."""
    is_active: bool = True
    sequence: int = 0


class BaseUpdateSchema(BaseModel):
    """Base schema for updating entities with optional fields."""
    is_active: Optional[bool] = None
    sequence: Optional[int] = None


class BaseInDB(BaseSchema):
    """Base schema with database audit fields."""
    id: int = Field(..., ge=1, description="Unique identifier")
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    is_active: bool
    sequence: int

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
