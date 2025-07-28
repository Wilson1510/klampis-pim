from pydantic import Field, StrictStr, StrictBool
from typing import Optional

from app.schemas.base import BaseSchema, StrictPositiveInt


class ImageCreate(BaseSchema):
    """Schema for creating an image nested within another model."""
    file: StrictStr = Field(..., min_length=1, max_length=255)
    title: Optional[StrictStr] = Field(default=None, min_length=1, max_length=100)
    is_primary: StrictBool = False


class ImageUpdate(BaseSchema):
    """Schema for updating an existing image nested within another model."""
    id: StrictPositiveInt
    file: Optional[StrictStr] = Field(default=None, min_length=1, max_length=255)
    title: Optional[StrictStr] = Field(default=None, min_length=1, max_length=100)
    is_primary: Optional[StrictBool] = None


class ImageSummary(BaseSchema):
    """Schema for image summary."""
    id: int
    file: str
    title: Optional[str] = None
    is_primary: bool

    model_config = {"from_attributes": True}
