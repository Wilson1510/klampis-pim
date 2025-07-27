from sqlalchemy import Column, Integer, ForeignKey, Table

from app.core.base import Base

# Junction table for Many-to-Many relationship between AttributeSets and Attributes
attribute_set_attribute = Table(
    'attribute_set_attribute',
    Base.metadata,
    Column(
        'attribute_set_id', Integer, ForeignKey('attribute_sets.id'), primary_key=True
    ),
    Column('attribute_id', Integer, ForeignKey('attributes.id'), primary_key=True)
)
