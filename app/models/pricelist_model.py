from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.core.base import Base


class Pricelists(Base):
    """
    Pricelists model representing price lists.

    This model stores price lists. Each price list can have multiple price
    details, and each price detail belongs to one price list.
    """

    name = Column(String(50), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    price_details = relationship(
        "PriceDetails",
        back_populates="pricelist"
    )

    def __str__(self) -> str:
        """Return a string representation of the Pricelists model."""
        return f"Pricelists({self.name})"

    def __repr__(self) -> str:
        """Return a string representation of the Pricelists model."""
        return self.__str__()
