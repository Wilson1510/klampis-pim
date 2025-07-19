from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from app.core.base import Base


class DataType(str, Enum):
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"


class Attributes(Base):
    """
    Attributes model representing attributes for SKUs.

    This model stores attribute information and establishes relationships
    with attribute sets and sku attribute values. Each attribute belongs
    to one or more attribute sets and can have multiple sku attribute values.
    """
    name = Column(String(50), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    data_type = Column(
        ENUM(DataType),
        nullable=False,
        index=True,
        default=DataType.TEXT
    )
    uom = Column(String(15), nullable=True)

    # Relationships
    attribute_sets = relationship(
        "AttributeSets",
        secondary="attribute_set_attribute",
        back_populates="attributes"
    )
    sku_attribute_values = relationship(
        "SkuAttributeValue",
        back_populates="attribute"
    )

    @staticmethod
    def validate_value_for_data_type(value: str, data_type: DataType) -> bool:
        """
        Validate if a string value is compatible with the specified data type.
        Returns True if valid, False otherwise.
        """
        if not value:
            return True  # Allow empty values

        try:
            if data_type == DataType.TEXT:
                return True  # Any string is valid for TEXT

            elif data_type == DataType.NUMBER:
                float(value)  # Try to convert to float
                return True

            elif data_type == DataType.BOOLEAN:
                # Accept common boolean representations
                lower_value = value.lower().strip()
                return lower_value in ['true', 'false']

            elif data_type == DataType.DATE:
                # Try to parse as ISO date format
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                return True

        except (ValueError, TypeError):
            return False

    @staticmethod
    def convert_value_to_python(value: str, data_type: DataType):
        """
        Convert string value to appropriate Python type based on data_type.
        Used for validation and processing.
        """
        if not value:
            return None

        if data_type == DataType.TEXT:
            return value

        elif data_type == DataType.NUMBER:
            return float(value)

        elif data_type == DataType.BOOLEAN:
            lower_value = value.lower().strip()
            return lower_value == 'true'

        elif data_type == DataType.DATE:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))

    def __str__(self) -> str:
        """String representation of the attribute."""
        return f"Attributes({self.name})"

    def __repr__(self) -> str:
        """Official string representation of the attribute."""
        return self.__str__()
