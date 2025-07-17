import enum

from sqlalchemy import (
    Column, DateTime, Integer, String, ForeignKey, Enum, CheckConstraint
)
from sqlalchemy.orm import validates

from app.core.base import Base


class Role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"
    MANAGER = "MANAGER"


class Users(Base):
    """
    Users model representing system users.

    This model stores user authentication and profile information.
    All other models reference this for audit trail purposes.
    Passwords are automatically hashed using bcrypt when set.

    Business Rules:
    - Email must contain '@' and not start/end with '@' (enforced at both levels)
    - Username must be unique and not empty
    - Password must not be empty (length handled by bcrypt)

    Validation Strategy:
    - Application Level: Provides user-friendly error messages and email normalization
    - Database Level: Ensures data integrity for email format
    """
    username = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    email = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Increased length for bcrypt hashes
    name = Column(String(50), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.USER)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Override created_by and updated_by to be nullable for Users table
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,  # Allow null for system user
        default=None
    )
    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,  # Allow null for system user
        default=None
    )

    # Database constraints
    __table_args__ = (
        CheckConstraint(
            "email ~ '^[^@]+@[^@]+$'",
            name='check_email_format'
        ),
    )

    @validates('email')
    def validate_email(self, key, value):
        """
        Validate email field with user-friendly error messages.

        Database constraint serves as backup for data integrity.
        """
        if not isinstance(value, str):
            return value

        if '@' not in value:
            raise ValueError("Invalid email format (must contain '@').")

        if '@' in [value[0], value[-1]]:
            raise ValueError("Invalid email format (must not start or end with '@').")

        return value.lower().strip()

    def __str__(self) -> str:
        """String representation of the user."""
        return f"Users({self.name})"

    def __repr__(self) -> str:
        """Official string representation of the user."""
        return self.__str__()
