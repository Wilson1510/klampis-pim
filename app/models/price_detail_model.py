from sqlalchemy import (
    Column, Integer, Numeric, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.core.base import Base


class PriceDetails(Base):
    """
    PriceDetails model representing price details for SKUs.

    This model stores price details for SKUs in different pricelists. Each SKU can have
    multiple price details (one per pricelist and quantity tier), and each price detail
    belongs to one SKU and one pricelist.

    Business Rules:
    - Price must be greater than zero (enforced at both app and DB level)
    - Minimum quantity must be greater than zero (enforced at both app and DB level)
    - Each combination of (sku_id, pricelist_id, minimum_quantity) must be unique

    Validation Strategy:
    - Application Level: Provides user-friendly error messages and early validation
    - Database Level: Ensures data integrity even if application validation is bypassed
    """

    price = Column(Numeric(15, 2), nullable=False, index=True)
    minimum_quantity = Column(Integer, nullable=False, default=1, index=True)

    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False, index=True)
    pricelist_id = Column(
        Integer,
        ForeignKey("pricelists.id"),
        nullable=False,
        index=True
    )

    sku = relationship("Skus", back_populates="price_details")
    pricelist = relationship("Pricelists", back_populates="price_details")

    # Table constraints - Database level validation
    __table_args__ = (
        # Unique constraint for business rule
        UniqueConstraint(
            'minimum_quantity',
            'sku_id',
            'pricelist_id',
            name='uq_price_detail'
        ),
    )

    def __str__(self) -> str:
        """Return a string representation of the PriceDetails model."""
        return f"PriceDetails({self.price}, {self.minimum_quantity})"

    def __repr__(self) -> str:
        """Return a string representation of the PriceDetails model."""
        return self.__str__()
