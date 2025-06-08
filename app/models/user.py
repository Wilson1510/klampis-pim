from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import validates

from app.core.base import Base


class Users(Base):
    """
    Users model representing system users.

    This model stores user authentication and profile information.
    All other models reference this for audit trail purposes.

    Attributes:
        id: Unique identifier for the user
        date_joined: Date and time when the user was added to the system
        username: Unique username for authentication
        password: Hashed password for authentication
        name: Display name of the user
        role: User role determining permissions
        is_active: Flag indicating if the user is active
    """
    username = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    password = Column(String(100), nullable=False)
    name = Column(String(50), nullable=False)
    role = Column(String, nullable=False, default="USER")

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

    @validates('role')
    def validate_role(self, key, value):
        """Validate role field."""
        if value not in ["USER", "ADMIN", "SYSTEM", "MANAGER"]:
            raise ValueError("Invalid role")
        return value

    def __str__(self) -> str:
        """String representation of the user."""
        return f"User(id={self.id}, username='{self.username}', name='{self.name}')"

    def __repr__(self) -> str:
        """Official string representation of the user."""
        return self.__str__()
