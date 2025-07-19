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

    def __str__(self) -> str:
        """String representation of the product."""
        return f"Products({self.name})"

    def __repr__(self) -> str:
        """Official string representation of the product."""
        return self.__str__()
