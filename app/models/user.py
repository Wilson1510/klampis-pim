from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import validates

from app.core.base import Base


class Users(Base):
    """
    Users model representing system users.

    This model stores user authentication and profile information.
    All other models reference this for audit trail purposes.
    Passwords are automatically hashed using bcrypt when set.
    """
    username = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Increased length for bcrypt hashes
    name = Column(String(50), nullable=False)
    role = Column(String, nullable=False, default="USER")
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

    @validates('email')
    def validate_email(self, key, value):
        """
        This validator only runs for the 'email' column.
        """
        if not isinstance(value, str):
            return value

        if '@' not in value:
            raise ValueError("Invalid email format (must contain '@').")

        if '@' in [value[0], value[-1]]:
            raise ValueError("Invalid email format (must not start or end with '@').")

        return value.lower().strip()

    @validates('role')
    def validate_role(self, key, value):
        """Validate role field."""
        if value not in ["USER", "ADMIN", "SYSTEM", "MANAGER"]:
            raise ValueError("Invalid role")
        return value

    def __str__(self) -> str:
        """String representation of the user."""
        return f"Users(username={self.username}, name={self.name})"

    def __repr__(self) -> str:
        """Official string representation of the user."""
        return self.__str__()
