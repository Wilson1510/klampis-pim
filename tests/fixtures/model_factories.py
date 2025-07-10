"""
Factory fixtures for creating test objects with flexible parameters.

This module provides factory fixtures that can create model instances
with default values while allowing customization through kwargs.
All factories use the flexible pattern with {**defaults, **kwargs}
for maximum safety and maintainability.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category_type_model import CategoryTypes
from app.models.category_model import Categories
from app.models.supplier_model import Suppliers, CompanyType
from app.models.product_model import Products
from app.models.sku_model import Skus
from app.models.attribute_model import Attributes
from tests.utils.model_test_utils import save_object


@pytest.fixture
async def category_type_factory(db_session: AsyncSession):
    """
    Factory for creating CategoryTypes with flexible parameters.

    Usage:
        # Minimal (uses defaults)
        category_type = await category_type_factory()

        # With custom name
        category_type = await category_type_factory(name="Electronics")

        # With all parameters
        category_type = await category_type_factory(
            name="Food & Beverages",
            slug="food-beverages"  # Will be auto-generated if not provided
        )
    """
    async def _factory(**kwargs):
        # Define default values for required fields
        defaults = {
            "name": "Test Category Type"
        }

        # Merge defaults with provided kwargs (kwargs override defaults)
        params = {**defaults, **kwargs}

        # Create the object with merged parameters
        category_type = CategoryTypes(**params)

        # Save and return
        await save_object(db_session, category_type)
        return category_type

    return _factory


@pytest.fixture
async def category_factory(db_session: AsyncSession, category_type_factory):
    """
    Factory for creating Categories with flexible parameters.

    Usage:
        # Minimal (creates parent category with auto-generated category_type)
        category = await category_factory()

        # Child category with specific parent
        parent = await category_factory(name="Electronics")
        child = await category_factory(
            name="Mobile Phones",
            parent_id=parent.id
        )

        # With custom category_type
        category_type = await category_type_factory(name="Food")
        category = await category_factory(
            name="Beverages",
            category_type=category_type
        )
    """
    async def _factory(**kwargs):
        # Handle special parameters that need processing
        category_type = kwargs.pop('category_type', None)
        parent_id = kwargs.get('parent_id', None)

        # Define default values
        defaults = {
            "name": "Test Category",
            "description": None
        }

        # Handle business logic for category hierarchy
        if parent_id is not None:
            # Child category - should not have category_type_id
            defaults["parent_id"] = parent_id
            defaults["category_type_id"] = None
        else:
            # Parent category - needs category_type_id
            if category_type is None:
                category_type = await category_type_factory()
            defaults["category_type_id"] = category_type.id
            defaults["parent_id"] = None

        # Merge defaults with provided kwargs
        params = {**defaults, **kwargs}

        # Create the object
        category = Categories(**params)

        # Save and return
        await save_object(db_session, category)
        return category

    return _factory


@pytest.fixture
async def supplier_factory(db_session: AsyncSession):
    """
    Factory for creating Suppliers with flexible parameters.

    Usage:
        # Minimal (uses defaults)
        supplier = await supplier_factory()

        # With custom parameters
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            company_type=CompanyType.PT,
            contact="081234567890",
            email="info@majujaya.com"
        )
    """
    async def _factory(**kwargs):
        # Define default values
        defaults = {
            "name": "Test Supplier",
            "company_type": CompanyType.PT,
            "address": "Test Address",
            "contact": "081234567890",
            "email": "test@supplier.com"
        }

        # Merge defaults with provided kwargs
        params = {**defaults, **kwargs}

        # Create the object
        supplier = Suppliers(**params)

        # Save and return
        await save_object(db_session, supplier)
        return supplier

    return _factory


@pytest.fixture
async def product_factory(db_session: AsyncSession, category_factory, supplier_factory):
    """
    Factory for creating Products with flexible parameters.

    Usage:
        # Minimal (creates category and supplier automatically)
        product = await product_factory()

        # With existing category and supplier
        category = await category_factory(name="Electronics")
        supplier = await supplier_factory(name="PT Electronics")
        product = await product_factory(
            name="Smartphone",
            category=category,
            supplier=supplier
        )

        # With IDs directly
        product = await product_factory(
            name="Laptop",
            category_id=1,
            supplier_id=2
        )
    """
    async def _factory(**kwargs):
        # Handle special parameters that need processing
        category = kwargs.pop('category', None)
        supplier = kwargs.pop('supplier', None)

        # Define default values
        defaults = {
            "name": "Test Product",
            "description": None
        }

        # Handle category dependency
        if 'category_id' not in kwargs:
            if category is None:
                category = await category_factory()
            defaults["category_id"] = category.id

        # Handle supplier dependency
        if 'supplier_id' not in kwargs:
            if supplier is None:
                supplier = await supplier_factory()
            defaults["supplier_id"] = supplier.id

        # Merge defaults with provided kwargs
        params = {**defaults, **kwargs}

        # Create the object
        product = Products(**params)

        # Save and return
        await save_object(db_session, product)
        return product

    return _factory


@pytest.fixture
async def sku_factory(db_session: AsyncSession, product_factory):
    """
    Factory for creating Skus with flexible parameters.

    Usage:
        # Minimal (creates product automatically)
        sku = await sku_factory()

        # With existing product
        product = await product_factory(name="Smartphone")
        sku = await sku_factory(
            name="iPhone 15 Pro 256GB",
            product=product
        )

        # With custom SKU number
        sku = await sku_factory(
            name="Custom SKU",
            sku_number="ABC1234567"
        )
    """
    async def _factory(**kwargs):
        # Handle special parameters that need processing
        product = kwargs.pop('product', None)

        # Define default values
        defaults = {
            "name": "Test SKU",
            "description": None
        }

        # Handle product dependency
        if 'product_id' not in kwargs:
            if product is None:
                product = await product_factory()
            defaults["product_id"] = product.id

        # Merge defaults with provided kwargs
        params = {**defaults, **kwargs}

        # Create the object
        sku = Skus(**params)

        # Save and return
        await save_object(db_session, sku)
        return sku

    return _factory


@pytest.fixture
async def attribute_factory(db_session: AsyncSession):
    """
    Factory for creating Attributes with flexible parameters.

    Usage:
        # Minimal (uses defaults)
        attribute = await attribute_factory()

        # With custom parameters
        attribute = await attribute_factory(
            name="Color",
            data_type=DataType.TEXT,
            uom="RGB"
        )

        # Number attribute
        attribute = await attribute_factory(
            name="Weight",
            data_type=DataType.NUMBER,
            uom="kg"
        )
    """
    async def _factory(**kwargs):
        # Define default values
        defaults = {
            "name": "Test Attribute"
        }

        # Merge defaults with provided kwargs
        params = {**defaults, **kwargs}

        # Create the object
        attribute = Attributes(**params)

        # Save and return
        await save_object(db_session, attribute)
        return attribute

    return _factory
