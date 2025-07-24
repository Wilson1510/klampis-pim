from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, StrictBool, StrictInt, Field

StrictNonNegativeInt = Annotated[StrictInt, Field(ge=0)]
StrictPositiveInt = Annotated[StrictInt, Field(gt=0)]


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
