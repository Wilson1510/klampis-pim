from sqlalchemy import Column, String, Text
from sqlalchemy.orm import validates, relationship

from app.core.base import Base


class Suppliers(Base):
    """
    Suppliers model representing product suppliers.

    This model stores supplier information including company details,
    contact information, and addresses. Suppliers can provide multiple
    products to the system.
    """
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    company_type = Column(String(50), nullable=False)
    address = Column(Text, nullable=True)
    contact = Column(String(13), unique=True, nullable=False, index=True)
    email = Column(String(50), unique=True, nullable=False, index=True)

    # Relationships
    products = relationship("Products", back_populates="supplier")

    @validates('contact')
    def validate_contact(self, key, value):
        """Validate contact field."""
        if not isinstance(value, str):
            return value

        if not value.strip().isdigit():
            raise ValueError("Contact must contain only digits")
        return value.strip()

    @validates('email')
    def validate_email(self, key, value):
        """Validate email field."""
        if not isinstance(value, str):
            return value

        if '@' not in value:
            raise ValueError("Invalid email format (must contain '@').")

        if '@' in [value[0], value[-1]]:
            raise ValueError("Invalid email format (must not start or end with '@').")

        return value.lower().strip()

    @validates('company_type')
    def validate_company_type(self, key, value):
        """Validate company_type field."""
        if not isinstance(value, str):
            return value
        if value.upper().strip() not in ["INDIVIDUAL", "PT", "CV", "UD"]:
            raise ValueError("Invalid company type")
        return value.upper().strip()

    def __str__(self) -> str:
        """String representation of the supplier."""
        return f"Suppliers({self.name})"

    def __repr__(self) -> str:
        """Official string representation of the supplier."""
        return self.__str__()
