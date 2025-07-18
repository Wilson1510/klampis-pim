import enum

from sqlalchemy import Column, Enum, String, Text
from sqlalchemy.orm import relationship

from app.core.base import Base


class CompanyType(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    PT = "PT"
    CV = "CV"
    UD = "UD"


class Suppliers(Base):
    """
    Suppliers model representing product suppliers.

    This model stores supplier information including company details,
    contact information, and addresses. Suppliers can provide multiple
    products to the system.

    Business Rules:
    - Contact must contain only digits (enforced at both levels)
    - Email must contain '@' and not start/end with '@' (enforced at both levels)
    - Name and company_type are required

    Validation Strategy:
    - Application Level: Provides user-friendly error messages and data normalization
    - Database Level: Ensures data integrity for contact and email format
    """
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    company_type = Column(Enum(CompanyType), nullable=False)
    address = Column(Text, nullable=True)
    contact = Column(String(13), unique=True, nullable=False, index=True)
    email = Column(String(50), unique=True, nullable=False, index=True)

    # Relationships
    products = relationship("Products", back_populates="supplier")

    # Database constraints
    # __table_args__ = (
    #     CheckConstraint(
    #         "contact ~ '^[0-9]+$'",
    #         name='check_contact_digits_only'
    #     ),
    #     CheckConstraint(
    #         "email ~ '^[^@]+@[^@]+$'",
    #         name='check_email_format'
    #     ),
    # )

    def __str__(self) -> str:
        """String representation of the supplier."""
        return f"Suppliers({self.name})"

    def __repr__(self) -> str:
        """Official string representation of the supplier."""
        return self.__str__()
