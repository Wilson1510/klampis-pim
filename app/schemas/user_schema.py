from typing import Optional, Literal
from datetime import datetime
from pydantic import EmailStr, StrictStr, Field

from app.schemas.base import BaseSchema, BaseCreateSchema, BaseUpdateSchema, BaseInDB


class UserBase(BaseSchema):
    """Base user schema with common fields."""
    username: StrictStr = Field(..., min_length=3, max_length=20)
    email: EmailStr = Field(..., min_length=1, max_length=50)
    name: StrictStr = Field(..., min_length=1, max_length=50)
    role: Literal["USER", "ADMIN", "SYSTEM", "MANAGER"] = Field(default="USER")


class UserCreate(UserBase, BaseCreateSchema):
    """Schema for creating a new user."""
    password: StrictStr = Field(..., min_length=6)


class UserUpdate(UserBase, BaseUpdateSchema):
    """Schema for updating a user."""
    username: Optional[StrictStr] = Field(default=None, min_length=3, max_length=20)
    email: Optional[EmailStr] = Field(default=None, min_length=1, max_length=50)
    name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=50)
    role: Optional[Literal["USER", "ADMIN", "SYSTEM", "MANAGER"]] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase, BaseInDB):
    """Schema for user response."""
    last_login: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = {
        "from_attributes": True
    }


class UserLogin(BaseSchema):
    """Schema for user login."""
    username: StrictStr
    password: StrictStr


class UserChangePassword(BaseSchema):
    """Schema for changing user password."""
    current_password: StrictStr
    new_password: StrictStr


class Token(BaseSchema):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseSchema):
    """Schema for token refresh request."""
    refresh_token: str
