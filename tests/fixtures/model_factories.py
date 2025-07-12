"""
Factory fixtures for creating test objects with flexible parameters.

This module provides factory fixtures that can create model instances
with default values while allowing customization through kwargs.
All factories use the flexible pattern with {**defaults, **kwargs}
for maximum safety and maintainability.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category_type_model import CategoryTypes
from app.models.category_model import Categories
from app.models.supplier_model import Suppliers, CompanyType
from app.models.product_model import Products
from app.models.sku_model import Skus
from app.models.attribute_model import Attributes
from app.models.attribute_set_model import AttributeSets
from app.models.sku_attribute_value_model import SkuAttributeValue
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
        # Handle relationship objects first
        parent = kwargs.pop('parent', None)
        if parent:
            kwargs['parent_id'] = parent.id  # Ensure parent_id is set

        # Define default values
        defaults = {
            "name": "Test Category",
            "description": None
        }

        # Handle business logic for category hierarchy
        if 'parent_id' in kwargs and kwargs['parent_id'] is not None:
            # Child category - should not have category_type_id
            defaults["parent_id"] = kwargs['parent_id']
            defaults["category_type_id"] = None
        else:
            # Parent category - needs category_type_id
            defaults["parent_id"] = None

            # Handle category_type dependency with priority:
            # 1. Direct object, 2. Direct ID, 3. Get-or-Create
            category_type = kwargs.pop('category_type', None)
            if category_type:
                defaults['category_type_id'] = category_type.id
            elif 'category_type_id' not in kwargs:
                # Get or Create a default if no ID was provided
                stmt = select(CategoryTypes).where(
                    CategoryTypes.name == "Test Category Type"
                )
                result = await db_session.execute(stmt)
                existing_type = result.scalar_one_or_none()
                if existing_type:
                    defaults['category_type_id'] = existing_type.id
                else:
                    new_type = await category_type_factory()
                    defaults['category_type_id'] = new_type.id

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
        if category:
            kwargs['category_id'] = category.id

        supplier = kwargs.pop('supplier', None)
        if supplier:
            kwargs['supplier_id'] = supplier.id

        # Define default values
        defaults = {
            "name": "Test Product",
            "description": None
        }

        # Handle category dependency (get-or-create if not provided)
        if 'category_id' not in kwargs:
            stmt = select(Categories).where(Categories.name == "Test Category")
            result = await db_session.execute(stmt)
            existing_category = result.scalar_one_or_none()
            if existing_category:
                defaults['category_id'] = existing_category.id
            else:
                new_category = await category_factory()
                defaults['category_id'] = new_category.id

        # Handle supplier dependency (get-or-create if not provided)
        if 'supplier_id' not in kwargs:
            stmt = select(Suppliers).where(Suppliers.name == "Test Supplier")
            result = await db_session.execute(stmt)
            existing_supplier = result.scalar_one_or_none()
            if existing_supplier:
                defaults['supplier_id'] = existing_supplier.id
            else:
                new_supplier = await supplier_factory()
                defaults['supplier_id'] = new_supplier.id

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
        # Handle relationship object first
        product = kwargs.pop('product', None)
        if product:
            kwargs['product_id'] = product.id

        # Define default values
        defaults = {
            "name": "Test SKU",
            "description": None
        }

        # Handle product dependency (get-or-create if not provided)
        if 'product_id' not in kwargs:
            stmt = select(Products).where(Products.name == "Test Product")
            result = await db_session.execute(stmt)
            existing_product = result.scalar_one_or_none()
            if existing_product:
                defaults['product_id'] = existing_product.id
            else:
                new_product = await product_factory()
                defaults['product_id'] = new_product.id

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


@pytest.fixture
async def attribute_set_factory(db_session: AsyncSession):
    """
    Factory for creating AttributeSets with flexible parameters.
    """
    async def _factory(**kwargs):
        # Define default values
        defaults = {
            "name": "Test Attribute Set"
        }

        # Merge defaults with provided kwargs
        params = {**defaults, **kwargs}

        # Create the object
        attribute_set = AttributeSets(**params)

        # Save and return
        await save_object(db_session, attribute_set)
        return attribute_set

    return _factory


@pytest.fixture
async def sku_attribute_value_factory(
    db_session: AsyncSession, sku_factory, attribute_factory
):
    """
    Factory for creating SkuAttributeValue with flexible parameters.

    Usage:
        # Minimal (creates sku and attribute automatically)
        sku_attr_value = await sku_attribute_value_factory()

        # With existing sku and attribute
        sku = await sku_factory(name="Test SKU")
        attribute = await attribute_factory(name="Color")
        sku_attr_value = await sku_attribute_value_factory(
            value="Red",
            sku=sku,
            attribute=attribute
        )

        # With IDs directly
        sku_attr_value = await sku_attribute_value_factory(
            value="Blue",
            sku_id=1,
            attribute_id=2
        )

        # With None value
        sku_attr_value = await sku_attribute_value_factory(value=None)
    """
    async def _factory(**kwargs):
        # Handle relationship objects first
        sku = kwargs.pop('sku', None)
        if sku:
            kwargs['sku_id'] = sku.id

        attribute = kwargs.pop('attribute', None)
        if attribute:
            kwargs['attribute_id'] = attribute.id

        # Define default values
        defaults = {
            "value": "Test Value"
        }

        # Handle sku dependency (get-or-create if not provided)
        if 'sku_id' not in kwargs:
            stmt = select(Skus).where(Skus.name == "Test SKU")
            result = await db_session.execute(stmt)
            existing_sku = result.scalar_one_or_none()
            if existing_sku:
                defaults['sku_id'] = existing_sku.id
            else:
                new_sku = await sku_factory()
                defaults['sku_id'] = new_sku.id

        # Handle attribute dependency (get-or-create if not provided)
        if 'attribute_id' not in kwargs:
            stmt = select(Attributes).where(Attributes.name == "Test Attribute")
            result = await db_session.execute(stmt)
            existing_attribute = result.scalar_one_or_none()
            if existing_attribute:
                defaults['attribute_id'] = existing_attribute.id
            else:
                new_attribute = await attribute_factory()
                defaults['attribute_id'] = new_attribute.id

        # Merge defaults with provided kwargs
        params = {**defaults, **kwargs}

        # Create the object
        sku_attribute_value = SkuAttributeValue(**params)

        # Save and return
        await save_object(db_session, sku_attribute_value)
        return sku_attribute_value

    return _factory
