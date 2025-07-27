from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base import Base
from app.utils.mixins import Imageable


class Products(Base, Imageable):
    """
    Products model representing products in the system.

    This model stores product information and establishes relationships
    with categories, suppliers, and skus. Each product belongs
    to one category and one supplier, but can have multiple skus.
    """
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
        index=True
    )
    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True
    )

    # Relationships
    category = relationship("Categories", back_populates="products")
    supplier = relationship("Suppliers", back_populates="products")

    skus = relationship("Skus", back_populates="product")

    @property
    def full_path(self):
        """
        Computes the full hierarchical path from the root category to this product.
        The path includes the complete category hierarchy plus the product itself.
        The path is returned in order from root -> category -> ... -> product.
        """
        # Start with the category's full path
        path = []
        if self.category:
            path = self.category.full_path

        # Add the product to the path (product only has 3 keys: name, slug, type)
        product_item = {
            'name': self.name,
            'slug': self.slug,
            'type': 'Product'
        }
        path.append(product_item)

        return path

    def __str__(self) -> str:
        """String representation of the product."""
        return f"Products({self.name})"

    def __repr__(self) -> str:
        """Official string representation of the product."""
        return self.__str__()
