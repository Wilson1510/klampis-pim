from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import Session, validates
from sqlalchemy.ext.hybrid import hybrid_property
import re

from app.core.base import Base


class Images(Base):
    """
    Images model representing images in the system.
    """
    file = Column(String(255), nullable=False, unique=True)
    title = Column(String(100), nullable=True)
    is_primary = Column(Boolean, default=False)

    object_id = Column(Integer, nullable=False, index=True)
    content_type = Column(String(50), nullable=False, index=True)

    @hybrid_property
    def parent(self):
        """
        Dynamic property that automatically finds the parent model and retrieves the
        object.

        Dynamic Work:
        1. Get 'registry' from Base SQLAlchemy, which contains all registered models.
        2. Search for a model whose table name (__tablename__) matches the value of
        `self.content_type`.
        3. Once the model is found, it uses session.get() to retrieve the specific
        object.
        """
        session = Session.object_session(self)
        if not session:
            return None

        # Get 'registry' from Base class model this.
        # 'self.registry' refers to the registry where the Image model is defined.
        # 'self.registry.mappers' contains all information about the registered models.
        for mapper in self.registry.mappers:
            # Get the model class from the mapper
            cls = mapper.class_

            # Check if the model class has __tablename__ and matches the search type
            if hasattr(cls, '__tablename__') and cls.__tablename__ == self.content_type:
                # The correct model has been found!
                # Retrieve the object using session.get()
                return session.get(cls, self.object_id)

        # If the loop completes and no matching model is found, return None.
        return None

    @validates('file')
    def validate_file(self, key, value):
        """
        Validate file based on attribute's data_type. Create this validation to
        prevent validation checking at listeners.
        """
        value = value.strip()
        if value == "":
            raise ValueError(f"Column {key} cannot be empty")
        if not re.match(r'^[A-Za-z]', value[0]):
            raise ValueError(f"Column {key} must start with a letter")
        return value

    def __str__(self) -> str:
        """String representation of the image."""
        return f"Images({self.file})"

    def __repr__(self) -> str:
        """Official string representation of the image."""
        return self.__str__()
