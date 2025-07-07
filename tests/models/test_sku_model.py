from sqlalchemy import String, event, Text, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import pytest
import uuid

from app.core.base import Base
from app.models.category_type_model import CategoryTypes
from app.models.category_model import Categories
from app.models.product_model import Products
from app.models.sku_model import Skus
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


class TestSku:
    """Test suite for Sku model and relationships"""

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

        # Create a product
        self.test_product = Products(
            name="test product",
            description="test product description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, self.test_product)

        # Create skus
        self.test_sku1 = Skus(
            name="test sku 1",
            description="test sku 1 description",
            product_id=self.test_product.id
        )
        await save_object(db_session, self.test_sku1)

        self.test_sku2 = Skus(
            name="test sku 2",
            description="test sku 2 description",
            product_id=self.test_product.id
        )
        await save_object(db_session, self.test_sku2)

    def test_inheritance_from_base_model(self):
        """Test that Sku model inherits from Base model"""
        assert issubclass(Skus, Base)

    def test_fields_with_validation(self):
        """Test that Sku model has fields with validation"""
        assert hasattr(Skus, 'validate_sku_number')
        assert not hasattr(Skus, 'validate_name')
        assert len(Skus.__mapper__.validators) == 1

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(Skus.name, 'set', _set_slug)
        assert not event.contains(Skus, 'set', _set_slug)

    def test_name_field_properties(self):
        """Test the properties of the name field"""
        name_column = Skus.__table__.columns.get('name')
        assert name_column is not None
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 100
        assert name_column.nullable is False
        assert name_column.unique is None
        assert name_column.index is True
        assert name_column.default is None

    def test_slug_field_properties(self):
        """Test the properties of the slug field"""
        slug_column = Skus.__table__.columns.get('slug')
        assert slug_column is not None
        assert isinstance(slug_column.type, String)
        assert slug_column.type.length == 100
        assert slug_column.nullable is False
        assert slug_column.unique is True
        assert slug_column.index is True
        assert slug_column.default is None

    def test_description_field_properties(self):
        """Test the properties of the description field"""
        description_column = Skus.__table__.columns.get('description')
        assert description_column is not None
        assert isinstance(description_column.type, Text)
        assert description_column.nullable is True
        assert description_column.unique is None
        assert description_column.index is None
        assert description_column.default is None

    def test_sku_number_field_properties(self):
        """Test the properties of the sku_number field"""
        sku_number_column = Skus.__table__.columns.get('sku_number')
        assert sku_number_column is not None
        assert isinstance(sku_number_column.type, String)
        assert sku_number_column.type.length == 10
        assert sku_number_column.nullable is False
        assert sku_number_column.unique is True
        assert sku_number_column.index is True
        assert sku_number_column.default.is_callable is True

    def test_product_id_field_properties(self):
        """Test the properties of the product_id field"""
        product_id_column = Skus.__table__.columns.get('product_id')
        assert product_id_column is not None
        assert isinstance(product_id_column.type, Integer)
        assert product_id_column.nullable is False
        foreign_key = list(product_id_column.foreign_keys)[0]
        assert str(foreign_key.target_fullname) == "products.id"
        assert product_id_column.unique is None
        assert product_id_column.index is True
        assert product_id_column.default is None

    def test_relationships_with_other_models(self):
        """Test the relationships with other models"""
        assert_relationship(Skus, "product", "skus")

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_sku1)
        assert str_repr == "Skus(test sku 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        assert self.test_sku1.id == 1
        assert self.test_sku1.name == "test sku 1"
        assert self.test_sku1.slug == "test-sku-1"
        assert self.test_sku1.description == "test sku 1 description"
        assert self.test_sku1.sku_number is not None
        assert len(self.test_sku1.sku_number) == 10
        assert self.test_sku1.product_id == self.test_product.id
        assert self.test_sku1.product == self.test_product

        assert self.test_sku2.id == 2
        assert self.test_sku2.name == "test sku 2"
        assert self.test_sku2.slug == "test-sku-2"
        assert self.test_sku2.description == "test sku 2 description"
        assert self.test_sku2.sku_number is not None
        assert len(self.test_sku2.sku_number) == 10
        assert self.test_sku2.product_id == self.test_product.id
        assert self.test_sku2.product == self.test_product

        # sku_number should be unique
        assert self.test_sku1.sku_number != self.test_sku2.sku_number

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = Skus(
            name="test sku 3",
            description="test sku 3 description",
            product_id=self.test_product.id
        )
        await save_object(db_session, item)

        assert item.id == 3
        assert item.name == "test sku 3"
        assert item.slug == "test-sku-3"
        assert item.description == "test sku 3 description"
        assert item.sku_number is not None
        assert item.product_id == self.test_product.id
        assert await count_model_objects(db_session, Skus) == 3

        item_with_slug_and_sku = Skus(
            name="test sku 4",
            slug="slug-sku-4",
            sku_number="BE1258DFEE",
            description="test sku 4 description",
            product_id=self.test_product.id
        )
        await save_object(db_session, item_with_slug_and_sku)
        assert item_with_slug_and_sku.id == 4
        assert item_with_slug_and_sku.name == "test sku 4"
        # slug should be set to the slugified name, not the one provided
        assert item_with_slug_and_sku.slug == "test-sku-4"
        # sku_number should be set to the one provided
        assert item_with_slug_and_sku.sku_number == "BE1258DFEE"
        assert item_with_slug_and_sku.description == "test sku 4 description"
        assert item_with_slug_and_sku.product_id == self.test_product.id
        assert await count_model_objects(db_session, Skus) == 4

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(db_session, Skus, self.test_sku1.id)
        assert item.id == 1
        assert item.name == "test sku 1"
        assert item.slug == "test-sku-1"
        assert item.description == "test sku 1 description"
        assert item.product_id == self.test_product.id

        item = await get_object_by_id(db_session, Skus, self.test_sku2.id)
        assert item.id == 2
        assert item.name == "test sku 2"
        assert item.slug == "test-sku-2"
        assert item.description == "test sku 2 description"
        assert item.product_id == self.test_product.id

        items = await get_all_objects(db_session, Skus)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].name == "test sku 1"
        assert items[0].slug == "test-sku-1"
        assert items[0].description == "test sku 1 description"
        assert items[0].product_id == self.test_product.id

        assert items[1].id == 2
        assert items[1].name == "test sku 2"
        assert items[1].slug == "test-sku-2"
        assert items[1].description == "test sku 2 description"
        assert items[1].product_id == self.test_product.id

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(db_session, Skus, self.test_sku1.id)
        original_sku_number = item.sku_number

        item.name = "updated test sku 1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test sku 1"
        assert item.slug == "updated-test-sku-1"
        assert item.sku_number == original_sku_number  # should not change on update
        assert item.description == "test sku 1 description"
        assert item.product_id == self.test_product.id
        assert await count_model_objects(db_session, Skus) == 2

        item.slug = "updated-slug-sku-1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test sku 1"
        # slug should keep the same as it's generated from name
        assert item.slug == "updated-test-sku-1"
        assert await count_model_objects(db_session, Skus) == 2

        item.sku_number = uuid.uuid4().hex[:10].upper()
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test sku 1"
        assert item.sku_number is not None
        assert len(item.sku_number) == 10
        assert item.sku_number != original_sku_number

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_sku2)

        item = await get_object_by_id(db_session, Skus, self.test_sku2.id)
        assert item is None
        assert await count_model_objects(db_session, Skus) == 1

    """
    ================================================
    Relationship Tests (Skus -> Products)
    ================================================
    """

    @pytest.mark.asyncio
    async def test_sku_with_product_relationship(
        self, db_session: AsyncSession
    ):
        """Test sku with product relationship properly loads"""
        retrieved_sku = await get_object_by_id(
            db_session,
            Skus,
            self.test_sku1.id
        )

        assert retrieved_sku.product_id == self.test_product.id
        assert retrieved_sku.product == self.test_product
        assert retrieved_sku.product.name == "test product"

    @pytest.mark.asyncio
    async def test_sku_without_product_relationship(
        self, db_session: AsyncSession
    ):
        """Test sku without product relationship"""
        item = Skus(
            name="test sku without product",
            description="test description"
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)

    @pytest.mark.asyncio
    async def test_update_sku_to_different_product(
        self, db_session: AsyncSession
    ):
        """Test updating a sku to use a different product"""
        # Create another product
        another_product = Products(
            name="Another Test Product",
            description="another test product description",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, another_product)

        # Create sku with first product
        sku = Skus(
            name="test sku change product",
            description="test description",
            product_id=self.test_product.id
        )
        await save_object(db_session, sku)

        # Verify initially has first product
        assert sku.product_id == self.test_product.id
        assert sku.product == self.test_product
        assert sku.product.name == "test product"

        # Update to use different product
        sku.product_id = another_product.id
        await save_object(db_session, sku)

        # Verify product relationship is now the other one
        assert sku.product_id == another_product.id
        assert sku.product == another_product
        assert sku.product.name == "Another Test Product"

    @pytest.mark.asyncio
    async def test_create_sku_with_invalid_product_id(
        self, db_session: AsyncSession
    ):
        """Test creating sku with non-existent product_id raises error"""
        sku = Skus(
            name="test invalid product",
            description="test description",
            product_id=999  # Non-existent ID
        )

        with pytest.raises(IntegrityError):
            await save_object(db_session, sku)

    @pytest.mark.asyncio
    async def test_update_sku_with_invalid_product_id(
        self, db_session: AsyncSession
    ):
        """Test updating sku with non-existent product_id raises error"""
        sku = Skus(
            name="test invalid product update",
            description="test description",
            product_id=self.test_product.id
        )
        await save_object(db_session, sku)

        # Update with invalid product_id
        sku.product_id = 999  # Non-existent ID

        with pytest.raises(IntegrityError):
            await save_object(db_session, sku)

    @pytest.mark.asyncio
    async def test_delete_sku_with_product_relationship(
        self, db_session: AsyncSession
    ):
        """Test deleting a sku that has product relationship"""
        # Create sku with product
        sku = Skus(
            name="test delete with product",
            description="test description",
            product_id=self.test_product.id
        )
        await save_object(db_session, sku)

        product = await get_object_by_id(
            db_session,
            Products,
            self.test_product.id
        )

        await db_session.refresh(product, ['skus'])

        assert product.skus == [self.test_sku1, self.test_sku2, sku]

        # Delete the sku
        await delete_object(db_session, sku)

        # Verify sku is deleted
        deleted_sku = await get_object_by_id(
            db_session, Skus, sku.id
        )
        assert deleted_sku is None

        # Verify product still exists (should not be affected)
        await db_session.refresh(product, ['skus'])
        assert product is not None
        assert product.name == "test product"
        assert product.skus == [self.test_sku1, self.test_sku2]
