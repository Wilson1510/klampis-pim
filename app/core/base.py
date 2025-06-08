from typing import Any, Dict

from sqlalchemy import Column, DateTime, Boolean, func, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative

from app.core.config import settings


# Base class for all database models
@as_declarative()
class Base:
    """
    Base SQLAlchemy model for all database models in the application.

    Provides common columns and utilities:
    - Integer primary key
    - Created and updated timestamps
    - Created and updated by user
    - Active status flag
    - Sequence number
    - Common methods for serialization
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        default=settings.SYSTEM_USER_ID
    )
    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        default=settings.SYSTEM_USER_ID
    )
    is_active = Column(Boolean, default=True, nullable=False)
    sequence = Column(Integer, nullable=False, default=0)

    # Generate __tablename__ automatically based on class name
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name automatically from class name in snake_case
        format."""
        # Convert CamelCase to snake_case
        return ''.join(
            ['_' + c.lower() if c.isupper() else c for c in cls.__name__]
        ).lstrip('_')

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}(id={self.id})"

    def __repr__(self) -> str:
        """Official string representation of the model."""
        return self.__str__()
