from sqlalchemy import String, event, Text, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import pytest

from app.core.base import Base
from app.models.category_type_model import CategoryTypes
from app.models.category_model import Categories
from app.models.product_model import Products
from app.models.supplier_model import Suppliers
from app.core.listeners import _set_slug
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    assert_relationship,
    count_model_objects
)


class TestProduct:
    """Test suite for Product model and relationships"""

    @pytest.fixture(autouse=True)
    async def setup_objects(self, db_session: AsyncSession):
        """Setup method for the test suite"""
        # Create category type
        self.test_category_type = CategoryTypes(
            name="test category type"
        )
        await save_object(db_session, self.test_category_type)

        # Create category
        self.test_category = Categories(
            name="test category",
            description="test category description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, self.test_category)

        # Create supplier
        self.test_supplier = Suppliers(
            name="Test Supplier",
            company_type="PT",
            contact="1234567890123",
            email="test@supplier.com"
        )
        await save_object(db_session, self.test_supplier)

        # Create products
        self.test_product1 = Products(
            name="test product 1",
            description="test product 1 description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, self.test_product1)

        self.test_product2 = Products(
            name="test product 2",
            description="test product 2 description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, self.test_product2)

    def test_inheritance_from_base_model(self):
        """Test that Product model inherits from Base model"""
        assert issubclass(Products, Base)

    def test_fields_with_validation(self):
        """Test that Product model has fields with validation"""
        assert not hasattr(Products, 'validate_name')
        assert len(Products.__mapper__.validators) == 0

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(Products.name, 'set', _set_slug)
        assert not event.contains(Products, 'set', _set_slug)

    def test_name_field_properties(self):
        """Test the properties of the name field"""
        name_column = Products.__table__.columns.get('name')
        assert name_column is not None
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 100
        assert name_column.nullable is False
        assert name_column.unique is None
        assert name_column.index is True
        assert name_column.default is None

    def test_slug_field_properties(self):
        """Test the properties of the slug field"""
        slug_column = Products.__table__.columns.get('slug')
        assert slug_column is not None
        assert isinstance(slug_column.type, String)
        assert slug_column.type.length == 100
        assert slug_column.nullable is False
        assert slug_column.unique is True
        assert slug_column.index is True
        assert slug_column.default is None

    def test_description_field_properties(self):
        """Test the properties of the description field"""
        description_column = Products.__table__.columns.get('description')
        assert description_column is not None
        assert isinstance(description_column.type, Text)
        assert description_column.nullable is True
        assert description_column.unique is None
        assert description_column.index is None
        assert description_column.default is None

    def test_category_id_field_properties(self):
        """Test the properties of the category_id field"""
        category_id_column = Products.__table__.columns.get('category_id')
        assert category_id_column is not None
        assert isinstance(category_id_column.type, Integer)
        assert category_id_column.nullable is False
        foreign_key = list(category_id_column.foreign_keys)[0]
        assert str(foreign_key.target_fullname) == "categories.id"
        assert category_id_column.unique is None
        assert category_id_column.index is True
        assert category_id_column.default is None

    def test_supplier_id_field_properties(self):
        """Test the properties of the supplier_id field"""
        supplier_id_column = Products.__table__.columns.get('supplier_id')
        assert supplier_id_column is not None
        assert isinstance(supplier_id_column.type, Integer)
        assert supplier_id_column.nullable is False
        foreign_key = list(supplier_id_column.foreign_keys)[0]
        assert str(foreign_key.target_fullname) == "suppliers.id"
        assert supplier_id_column.unique is None
        assert supplier_id_column.index is True
        assert supplier_id_column.default is None

    def test_relationships_with_other_models(self):
        """Test the relationships with other models"""
        assert_relationship(Products, "category", "products")
        assert_relationship(Products, "supplier", "products")

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_product1)
        assert str_repr == "Products(test product 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        assert self.test_product1.id == 1
        assert self.test_product1.name == "test product 1"
        assert self.test_product1.slug == "test-product-1"
        assert self.test_product1.description == "test product 1 description"
        assert self.test_product1.category_id == self.test_category.id
        assert self.test_product1.category == self.test_category
        assert self.test_product1.supplier_id == self.test_supplier.id
        assert self.test_product1.supplier == self.test_supplier

        assert self.test_product2.id == 2
        assert self.test_product2.name == "test product 2"
        assert self.test_product2.slug == "test-product-2"
        assert self.test_product2.description == "test product 2 description"
        assert self.test_product2.category_id == self.test_category.id
        assert self.test_product2.category == self.test_category
        assert self.test_product2.supplier_id == self.test_supplier.id
        assert self.test_product2.supplier == self.test_supplier

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = Products(
            name="test product 3",
            description="test product 3 description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, item)

        assert item.id == 3
        assert item.name == "test product 3"
        assert item.slug == "test-product-3"
        assert item.description == "test product 3 description"
        assert item.category_id == self.test_category.id
        assert item.supplier_id == self.test_supplier.id
        assert await count_model_objects(db_session, Products) == 3

        item_with_slug = Products(
            name="test product 4",
            slug="slug-product-4",
            description="test product 4 description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, item_with_slug)
        assert item_with_slug.id == 4
        assert item_with_slug.name == "test product 4"
        # slug should be set to the slugified name
        assert item_with_slug.slug == "test-product-4"
        assert item_with_slug.description == "test product 4 description"
        assert item_with_slug.category_id == self.test_category.id
        assert item_with_slug.supplier_id == self.test_supplier.id
        assert await count_model_objects(db_session, Products) == 4

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(db_session, Products, self.test_product1.id)
        assert item.id == 1
        assert item.name == "test product 1"
        assert item.slug == "test-product-1"
        assert item.description == "test product 1 description"
        assert item.category_id == self.test_category.id
        assert item.supplier_id == self.test_supplier.id

        item = await get_object_by_id(db_session, Products, self.test_product2.id)
        assert item.id == 2
        assert item.name == "test product 2"
        assert item.slug == "test-product-2"
        assert item.description == "test product 2 description"
        assert item.category_id == self.test_category.id
        assert item.supplier_id == self.test_supplier.id

        items = await get_all_objects(db_session, Products)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].name == "test product 1"
        assert items[0].slug == "test-product-1"
        assert items[0].description == "test product 1 description"
        assert items[0].category_id == self.test_category.id
        assert items[0].supplier_id == self.test_supplier.id

        assert items[1].id == 2
        assert items[1].name == "test product 2"
        assert items[1].slug == "test-product-2"
        assert items[1].description == "test product 2 description"
        assert items[1].category_id == self.test_category.id
        assert items[1].supplier_id == self.test_supplier.id

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(db_session, Products, self.test_product1.id)
        item.name = "updated test product 1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test product 1"
        assert item.slug == "updated-test-product-1"
        assert item.description == "test product 1 description"
        assert item.category_id == self.test_category.id
        assert item.supplier_id == self.test_supplier.id
        assert await count_model_objects(db_session, Products) == 2

        item.slug = "updated-slug-product-1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test product 1"
        # slug keep the same
        assert item.slug == "updated-test-product-1"
        assert item.description == "test product 1 description"
        assert item.category_id == self.test_category.id
        assert item.supplier_id == self.test_supplier.id
        assert await count_model_objects(db_session, Products) == 2

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_product2)

        item = await get_object_by_id(db_session, Products, self.test_product2.id)
        assert item is None
        assert await count_model_objects(db_session, Products) == 1

    """
    ================================================
    Relationship Tests (Products -> Categories)
    ================================================
    """

    @pytest.mark.asyncio
    async def test_product_with_category_relationship(
        self, db_session: AsyncSession
    ):
        """Test product with category relationship properly loads"""
        retrieved_product = await get_object_by_id(
            db_session,
            Products,
            self.test_product1.id
        )

        assert retrieved_product.category_id == self.test_category.id
        assert retrieved_product.category == self.test_category
        assert retrieved_product.category.name == "test category"

    @pytest.mark.asyncio
    async def test_product_without_category_relationship(
        self, db_session: AsyncSession
    ):
        """Test product without category relationship"""
        item = Products(
            name="test product without category",
            description="test description",
            supplier_id=self.test_supplier.id
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)

    @pytest.mark.asyncio
    async def test_update_product_to_different_category(
        self, db_session: AsyncSession
    ):
        """Test updating a product to use a different category"""
        # Create another category
        another_category = Categories(
            name="another test category",
            description="another test category description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, another_category)

        # Create product with first category
        product = Products(
            name="test product change category",
            description="test description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, product)

        # Verify initially has first category
        assert product.category_id == self.test_category.id
        assert product.category == self.test_category
        assert product.category.name == "test category"

        # Update to use different category
        product.category_id = another_category.id
        await save_object(db_session, product)

        # Verify category relationship is now the other one
        assert product.category_id == another_category.id
        assert product.category == another_category
        assert product.category.name == "another test category"

    @pytest.mark.asyncio
    async def test_create_product_with_invalid_category_id(
        self, db_session: AsyncSession
    ):
        """Test creating product with non-existent category_id raises error"""
        product = Products(
            name="test invalid category",
            description="test description",
            category_id=999,  # Non-existent ID
            supplier_id=self.test_supplier.id
        )

        with pytest.raises(IntegrityError):
            await save_object(db_session, product)

    @pytest.mark.asyncio
    async def test_update_product_with_invalid_category_id(
        self, db_session: AsyncSession
    ):
        """Test updating product with non-existent category_id raises error"""
        product = Products(
            name="test invalid update",
            description="test description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, product)

        # Update with invalid category_id
        product.category_id = 999  # Non-existent ID

        with pytest.raises(IntegrityError):
            await save_object(db_session, product)

    @pytest.mark.asyncio
    async def test_delete_product_with_category_relationship(
        self, db_session: AsyncSession
    ):
        """Test deleting a product that has category relationship"""
        # Create product with category
        product = Products(
            name="test delete with category",
            description="test description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, product)

        category = await get_object_by_id(
            db_session,
            Categories,
            self.test_category.id
        )

        await db_session.refresh(category, ['products'])

        assert category.products == [self.test_product1, self.test_product2, product]

        # Delete the product
        await delete_object(db_session, product)

        # Verify product is deleted
        deleted_product = await get_object_by_id(
            db_session, Products, product.id
        )
        assert deleted_product is None

        # Verify category still exists (should not be affected)
        await db_session.refresh(category, ['products'])
        assert category is not None
        assert category.name == "test category"
        assert category.products == [self.test_product1, self.test_product2]

    """
    ================================================
    Relationship Tests (Products -> Suppliers)
    ================================================
    """

    @pytest.mark.asyncio
    async def test_product_with_supplier_relationship(
        self, db_session: AsyncSession
    ):
        """Test product with supplier relationship properly loads"""
        retrieved_product = await get_object_by_id(
            db_session,
            Products,
            self.test_product1.id
        )

        assert retrieved_product.supplier_id == self.test_supplier.id
        assert retrieved_product.supplier == self.test_supplier
        assert retrieved_product.supplier.name == "Test Supplier"

    @pytest.mark.asyncio
    async def test_product_without_supplier_relationship(
        self, db_session: AsyncSession
    ):
        """Test product without supplier relationship"""
        item = Products(
            name="test product without supplier",
            description="test description",
            category_id=self.test_category.id
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)

    @pytest.mark.asyncio
    async def test_update_product_to_different_supplier(
        self, db_session: AsyncSession
    ):
        """Test updating a product to use a different supplier"""
        # Create another supplier
        another_supplier = Suppliers(
            name="Another Test Supplier",
            company_type="CV",
            contact="9876543210987",
            email="another@supplier.com"
        )
        await save_object(db_session, another_supplier)

        # Create product with first supplier
        product = Products(
            name="test product change supplier",
            description="test description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, product)

        # Verify initially has first supplier
        assert product.supplier_id == self.test_supplier.id
        assert product.supplier == self.test_supplier
        assert product.supplier.name == "Test Supplier"

        # Update to use different supplier
        product.supplier_id = another_supplier.id
        await save_object(db_session, product)

        # Verify supplier relationship is now the other one
        assert product.supplier_id == another_supplier.id
        assert product.supplier == another_supplier
        assert product.supplier.name == "Another Test Supplier"

    @pytest.mark.asyncio
    async def test_create_product_with_invalid_supplier_id(
        self, db_session: AsyncSession
    ):
        """Test creating product with non-existent supplier_id raises error"""
        product = Products(
            name="test invalid supplier",
            description="test description",
            category_id=self.test_category.id,
            supplier_id=999  # Non-existent ID
        )

        with pytest.raises(IntegrityError):
            await save_object(db_session, product)

    @pytest.mark.asyncio
    async def test_update_product_with_invalid_supplier_id(
        self, db_session: AsyncSession
    ):
        """Test updating product with non-existent supplier_id raises error"""
        product = Products(
            name="test invalid supplier update",
            description="test description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, product)

        # Update with invalid supplier_id
        product.supplier_id = 999  # Non-existent ID

        with pytest.raises(IntegrityError):
            await save_object(db_session, product)

    @pytest.mark.asyncio
    async def test_delete_product_with_supplier_relationship(
        self, db_session: AsyncSession
    ):
        """Test deleting a product that has supplier relationship"""
        # Create product with supplier
        product = Products(
            name="test delete with supplier",
            description="test description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, product)

        supplier = await get_object_by_id(
            db_session,
            Suppliers,
            self.test_supplier.id
        )

        await db_session.refresh(supplier, ['products'])

        assert supplier.products == [self.test_product1, self.test_product2, product]

        # Delete the product
        await delete_object(db_session, product)

        # Verify product is deleted
        deleted_product = await get_object_by_id(
            db_session, Products, product.id
        )
        assert deleted_product is None

        # Verify supplier still exists (should not be affected)
        await db_session.refresh(supplier, ['products'])
        assert supplier is not None
        assert supplier.name == "Test Supplier"
        assert supplier.products == [self.test_product1, self.test_product2]
