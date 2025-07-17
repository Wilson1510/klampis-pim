from sqlalchemy import Column, String, Boolean, Integer, event, CheckConstraint
from sqlalchemy.orm import validates
from sqlalchemy.ext.asyncio import AsyncSession
import re

from app.core.base import Base


class Images(Base):
    """
    Images model representing images in the system.

    Business Rules:
    - File name must not be empty and must start with a letter (both levels)
    - Content type must be valid (enforced at application level)
    - Object ID must be positive

    Validation Strategy:
    - Application Level: User-friendly errors and content type validation
    - Database Level: Ensures data integrity for file format
    """
    CONTENT_TYPE_TO_CLASS = {}

    file = Column(String(255), nullable=False, unique=True)
    title = Column(String(100), nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)

    object_id = Column(Integer, nullable=False, index=True)
    content_type = Column(String(50), nullable=False, index=True)

    # Database constraints
    __table_args__ = (
        CheckConstraint(
            "file ~ '^[A-Za-z]'",
            name='check_file_starts_with_letter'
        ),
    )

    async def get_parent(self, session: AsyncSession):
        """
        Retrieve the parent object asynchronously.
        """
        cls = self.CONTENT_TYPE_TO_CLASS.get(self.content_type)
        if cls:
            return await session.get(cls, self.object_id)
        return None

    @validates('content_type')
    def validate_content_type(self, key, value):
        """
        Validate content type against registered model types.

        This validation is only at application level since content types
        are dynamically registered.
        """
        if value and value.strip() and value not in self.CONTENT_TYPE_TO_CLASS:
            raise ValueError(
                f"Invalid content_type: {value}. Must be one of "
                f"{set(self.CONTENT_TYPE_TO_CLASS.keys())}"
            )
        return value

    @validates('file')
    def validate_file(self, key, value):
        """
        Validate file name format.

        Database constraint serves as backup for data integrity.
        """
        value = value.strip()
        if value == "":
            raise ValueError(f"Column {key} cannot be empty")
        if not re.match(r'^[A-Za-z]', value[0]):
            raise ValueError(f"Column {key} must start with a letter")
        return value

    @event.listens_for(Base, 'class_instrument')
    def on_class_instrument(cls):
        if hasattr(cls, 'images') and hasattr(cls, '__tablename__'):
            Images.CONTENT_TYPE_TO_CLASS[cls.__tablename__] = cls

    def __str__(self) -> str:
        """String representation of the image."""
        return f"Images({self.file})"

    def __repr__(self) -> str:
        """Official string representation of the image."""
        return self.__str__()
