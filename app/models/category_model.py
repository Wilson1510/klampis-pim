from sqlalchemy import Column, String, Text, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.core.base import Base


class Categories(Base):
    """
    Categories model representing product categories.

    This model stores category information in a hierarchical structure.

    Business Rules (enforced by database constraint):
    - Top-level categories (parent_id IS NULL) MUST have category_type_id
    - Child categories (parent_id IS NOT NULL) MUST NOT have category_type_id

    Examples:
    - Electronics (category_type_id=1, parent_id=NULL) ✓
    - Mobile Phones (category_type_id=NULL, parent_id=electronics_id) ✓
    - Smartphones (category_type_id=NULL, parent_id=mobile_phones_id) ✓
    """
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_type_id = Column(
        Integer,
        ForeignKey("category_types.id"),
        nullable=True,  # Allow NULL for child categories
        index=True
    )
    parent_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,  # Allow NULL for top-level categories
        index=True
    )

    # Relationships
    category_type = relationship("CategoryTypes", back_populates="categories")
    parent = relationship(
        "Categories",
        remote_side="Categories.id",
        back_populates="children"
    )
    children = relationship("Categories", back_populates="parent")

    # Database constraint to enforce hierarchy rules
    __table_args__ = (
        CheckConstraint(
            '(parent_id IS NULL AND category_type_id IS NOT NULL) OR '
            '(parent_id IS NOT NULL AND category_type_id IS NULL)',
            name='chk_category_hierarchy_rule'
        ),
    )

    def __str__(self) -> str:
        """String representation of the category."""
        return f"Categories(name={self.name}, slug={self.slug})"

    def __repr__(self) -> str:
        """Official string representation of the category."""
        return self.__str__()
