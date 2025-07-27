from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.core.base import Base


class AttributeSets(Base):
    """
    AttributeSets model representing attribute sets in the system.

    This model stores attribute sets for categories. Each attribute set can have
    multiple attributes and can be associated with multiple categories.

    It has a many-to-many relationship with Attributes through the
    attribute_set_attributes junction table.
    """
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Relationships
    categories = relationship(
        "Categories",
        secondary="category_attribute_set",
        back_populates="attribute_sets"
    )
    attributes = relationship(
        "Attributes",
        secondary="attribute_set_attribute",
        back_populates="attribute_sets"
    )

    def __str__(self) -> str:
        """String representation of the attribute set."""
        return f"AttributeSets({self.name})"

    def __repr__(self) -> str:
        """Official string representation of the attribute set."""
        return self.__str__()
