import uuid

from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship, validates

from app.core.base import Base


class Skus(Base):
    """
    Skus model representing stock keeping units in the system.

    This model stores SKU information for products. Each SKU belongs to one product
    and represents a specific variant or item that can be individually tracked,
    priced, and sold. SKUs are the most granular level of inventory management.

    It has a many-to-many relationship with Attributes through the SkuAttributeValue
    association object, which stores the specific value for each attribute.
    """
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku_number = Column(
        String(10),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: uuid.uuid4().hex[:10].upper()
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    # Relationships
    product = relationship("Products", back_populates="skus")
    sku_attribute_values = relationship(
        "SkuAttributeValue",
        back_populates="sku"
    )
    price_details = relationship("PriceDetails", back_populates="sku")

    @validates('sku_number')
    def validate_sku_number(self, key, value):
        """
        Validates the SKU number format and length.

        The SKU number must be exactly 10 characters long and
        contain only hexadecimal characters (0-9, A-F).
        """
        if not isinstance(value, str):
            return value
        elif len(value) != 10:
            raise ValueError("SKU number must be exactly 10 characters long.")
        elif not all(c in '0123456789ABCDEF' for c in value.upper()):
            raise ValueError("SKU number must only contain 0-9 or A-F characters.")
        return value

    def __str__(self) -> str:
        """String representation of the SKU."""
        return f"Skus({self.name})"

    def __repr__(self) -> str:
        """Official string representation of the SKU."""
        return self.__str__()
