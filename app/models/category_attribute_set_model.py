from sqlalchemy import Column, Integer, ForeignKey, Table

from app.core.base import Base

# Junction table for Many-to-Many relationship between Categories and AttributeSets
category_attribute_set = Table(
    'category_attribute_set',
    Base.metadata,
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True),
    Column(
        'attribute_set_id', Integer, ForeignKey('attribute_sets.id'), primary_key=True
    )
)
