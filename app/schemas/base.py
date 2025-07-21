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
    id: int = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: int = Field(..., description="ID of user who created this record")
    updated_by: int = Field(..., description="ID of user who last updated this record")
    is_active: bool = Field(True, description="Whether the record is active")
    sequence: int = Field(0, description="Sequence number for ordering")

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
