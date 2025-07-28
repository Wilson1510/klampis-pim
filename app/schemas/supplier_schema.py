from typing import Optional, Literal

from pydantic import Field, StrictStr, EmailStr, field_validator

from app.schemas.base import (
    BaseSchema,
    BaseInDB,
    BaseCreateSchema,
    BaseUpdateSchema,
)


class SupplierBase(BaseSchema):
    """Base schema for Supplier with common fields."""
    # Use StrictStr to prevent automatic conversion from numbers
    name: StrictStr = Field(..., min_length=1, max_length=100)
    company_type: Literal["INDIVIDUAL", "PT", "CV", "UD"]
    address: Optional[str] = None
    contact: StrictStr = Field(..., min_length=10, max_length=13)
    email: EmailStr = Field(..., max_length=50)

    @field_validator('contact')
    @classmethod
    def validate_contact(cls, v: str) -> str:
        """
        Validates the contact number format.

        The contact must contain only digits and be 10-13 characters long.
        """

        v = v.strip()

        if not v.isdigit():
            raise ValueError("Contact must contain only digits")

        return v


class SupplierCreate(SupplierBase, BaseCreateSchema):
    """Schema for creating a new supplier.

    Used in: POST endpoints
    Contains: Only fields that client can/should provide
    Note: slug is auto-generated, not provided by client
    """
    pass


class SupplierUpdate(SupplierBase, BaseUpdateSchema):
    """Schema for updating an existing supplier.

    Used in: PUT/PATCH endpoints
    Contains: Optional fields that can be updated
    Note: slug is not updatable
    """
    name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=100)
    company_type: Optional[Literal["INDIVIDUAL", "PT", "CV", "UD"]] = None
    contact: Optional[StrictStr] = Field(default=None, min_length=10, max_length=13)
    email: Optional[EmailStr] = Field(default=None, max_length=50)

    @field_validator('contact')
    @classmethod
    def validate_contact_optional(cls, v: Optional[str]) -> Optional[str]:
        """
        Validates the contact number format if provided.
        """
        if v is None:
            return v

        v = v.strip()

        if not v.isdigit():
            raise ValueError("Contact must contain only digits")

        return v


class SupplierInDB(SupplierBase, BaseInDB):
    """Schema for Supplier as stored in database.

    Used in: Database operations, internal processing
    Contains: All database fields including auto-generated ones
    Purpose: Complete representation of database record
    """
    slug: str


class SupplierResponse(SupplierInDB):
    """Schema for Supplier API responses.

    Used in: API endpoint responses (GET, POST, PUT)
    Contains: All fields that should be returned to client
    Purpose: Explicit response model for API documentation
    """
    pass
