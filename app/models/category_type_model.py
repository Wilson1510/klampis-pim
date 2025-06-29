from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.core.base import Base


class CategoryTypes(Base):
    """
    CategoryTypes model representing product category types.

    This model stores category type information that will be used
    to categorize different categories. Each category belongs to one category type.
    For example: Electronics, Food, Beverages, etc.
    """
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Relationships
    categories = relationship("Categories", back_populates="category_type")

    def __str__(self) -> str:
        """String representation of the category type."""
        return f"CategoryTypes(name={self.name}, slug={self.slug})"

    def __repr__(self) -> str:
        """Official string representation of the category type."""
        return self.__str__()
