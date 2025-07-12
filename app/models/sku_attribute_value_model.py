from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship, validates

from app.core.base import Base


class SkuAttributeValue(Base):
    """
    SkuAttributeValue model representing attribute values for SKUs.

    This model stores attribute values for SKUs. Each SKU can have multiple
    attribute values, and each attribute value belongs to one SKU.
    """
    sku_id = Column(Integer, ForeignKey('skus.id'), nullable=False, index=True)
    attribute_id = Column(
        Integer,
        ForeignKey('attributes.id'),
        nullable=False,
        index=True
    )
    value = Column(String(50), nullable=False, index=True)

    # Relationships
    sku = relationship("Skus", back_populates="sku_attribute_values")
    attribute = relationship("Attributes", back_populates="sku_attribute_values")

    # Table constraints and indexes
    __table_args__ = (
        UniqueConstraint('sku_id', 'attribute_id', name='uq_sku_attribute'),
        Index('idx_sku_attribute_composite', 'sku_id', 'attribute_id'),
    )

    @validates('value')
    def validate_value(self, key, value):
        """Validate value based on attribute's data_type"""
        if not value:
            return value  # Allow empty values

        # Get the attribute to check its data_type
        if hasattr(self, 'attribute') and self.attribute:
            from app.models.attribute_model import Attributes

            if not Attributes.validate_value_for_data_type(
                value, self.attribute.data_type
            ):
                raise ValueError(
                    f"Value '{value}' is not valid for data type "
                    f"'{self.attribute.data_type}'"
                )

        return value

    def get_typed_value(self):
        """Get the value converted to its proper Python type"""
        if not self.value or not self.attribute:
            return None

        from app.models.attribute_model import Attributes
        return Attributes.convert_value_to_python(self.value, self.attribute.data_type)

    def __str__(self) -> str:
        """String representation of the SKU attribute value."""
        return (
            f"SkuAttributeValue(sku:{self.sku_id}, "
            f"attribute:{self.attribute_id}, value:{self.value})"
        )

    def __repr__(self) -> str:
        """Official string representation of the SKU attribute value."""
        return self.__str__()
