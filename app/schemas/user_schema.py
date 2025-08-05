from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, StrictStr, Field

from app.models.user_model import Role


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: StrictStr = Field(..., min_length=3, max_length=20)
    email: EmailStr = Field(..., min_length=1, max_length=50)
    name: StrictStr = Field(..., min_length=1, max_length=50)
    role: Role = Role.USER


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: StrictStr = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[StrictStr] = Field(default=None, min_length=3, max_length=20)
    email: Optional[EmailStr] = Field(default=None, min_length=1, max_length=50)
    name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=50)
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    sequence: int

    model_config = {
        "from_attributes": True
    }


class UserLogin(BaseModel):
    """Schema for user login."""
    username: StrictStr
    password: StrictStr


class UserChangePassword(BaseModel):
    """Schema for changing user password."""
    current_password: StrictStr
    new_password: StrictStr


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str
