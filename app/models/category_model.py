from sqlalchemy import Column, String, Text, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.core.base import Base
from app.utils.mixins import Imageable


class Categories(Base, Imageable):
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
    products = relationship("Products", back_populates="category")

    # Database constraint to enforce hierarchy rules
    __table_args__ = (
        CheckConstraint(
            '(parent_id IS NULL AND category_type_id IS NOT NULL) OR '
            '(parent_id IS NOT NULL AND category_type_id IS NULL)',
            name='check_category_hierarchy_rule'
        ),
        CheckConstraint(
            'id <> parent_id',
            name='check_category_no_self_reference'
        )
    )

    @property
    def full_path(self):
        """
        Computes the full hierarchical path from the root to this category.
        The path is returned in order from root -> parent -> self.
        """
        path = []
        current = self
        while current:
            if current.category_type:
                category_type = current.category_type.name
            else:
                category_type = None
            path_item = {
                'name': current.name,
                'slug': current.slug,
                'category_type': category_type,
                'type': 'Category'
            }
            path.append(path_item)
            current = current.parent
        # Reverse the path to get it from root -> self
        return list(reversed(path))

    def __str__(self) -> str:
        """String representation of the category."""
        return f"Categories({self.name})"

    def __repr__(self) -> str:
        """Official string representation of the category."""
        return self.__str__()
