from typing import Any, Dict, TypeVar

from sqlalchemy import Column, DateTime, Boolean, func, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative, validates
from app.utils.validators import FieldValidationMixin
from app.core.config import settings
# Generic type for model itself when used in class methods
ModelType = TypeVar("ModelType", bound="Base")


# Base class for all database models
@as_declarative()
class Base(FieldValidationMixin):
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

    @validates('is_active')
    def validate_is_active(self, key, value):
        """Validate the is_active field before assigning it"""
        return self.validate_boolean(key, value)
    
    @validates('sequence')
    def validate_sequence(self, key, value):
        """Validate the sequence field before assigning it"""
        return self.validate_integer(key, value)

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


class JSONBModel(Base):
    """
    Base model for entities with JSONB attributes.

    This class extends the Base model and adds a JSONB attributes field.
    Useful for models like Products that store category-specific attributes.
    """
    __abstract__ = True

    attributes = Column(JSONB, nullable=False)