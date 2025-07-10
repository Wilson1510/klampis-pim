from sqlalchemy import String, Text, event, select, Enum
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from app.models.supplier_model import Suppliers, CompanyType
from app.models.product_model import Products
from app.core.listeners import _set_slug
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    count_model_objects,
    assert_relationship
)


class TestSupplier:
    """Test suite for Supplier model and relationships"""
    @pytest.fixture(autouse=True)
    async def setup_objects(self, db_session: AsyncSession, supplier_factory):
        """Setup method for the test suite"""
        # Create supplier
        self.test_supplier1 = await supplier_factory(
            name="Test Supplier 1",
            company_type="PT",
            address="Test Address 1",
            contact="081234567890",
            email="test1@example.com"
        )

        self.test_supplier2 = await supplier_factory(
            name="Test Supplier 2",
            company_type="CV",
            address="Test Address 2",
            contact="081234567891",
            email="test2@example.com"
        )

    def test_inheritance_from_base_model(self):
        """Test that Supplier model inherits from Base model"""
        assert issubclass(Suppliers, Base)

    def test_fields_with_validation(self):
        """Test that the fields have the expected validation"""
        assert hasattr(Suppliers, 'validate_contact')
        assert hasattr(Suppliers, 'validate_email')
        assert not hasattr(Suppliers, 'validate_name')

        assert 'contact' in Suppliers.__mapper__.validators
        assert 'email' in Suppliers.__mapper__.validators
        assert 'name' not in Suppliers.__mapper__.validators

        assert len(Suppliers.__mapper__.validators) == 2

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(Suppliers.name, 'set', _set_slug)
        assert not event.contains(Suppliers, 'set', _set_slug)

    def test_name_field_properties(self):
        """Test the properties of the name field"""
        name_column = Suppliers.__table__.columns.get('name')
        assert name_column is not None
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 100
        assert name_column.nullable is False
        assert name_column.unique is None
        assert name_column.index is True
        assert name_column.default is None

    def test_slug_field_properties(self):
        """Test the properties of the slug field"""
        slug_column = Suppliers.__table__.columns.get('slug')
        assert slug_column is not None
        assert isinstance(slug_column.type, String)
        assert slug_column.type.length == 100
        assert slug_column.nullable is False
        assert slug_column.unique is True
        assert slug_column.index is True
        assert slug_column.default is None

    def test_company_type_field_properties(self):
        """Test the properties of the company_type field"""
        company_type_column = Suppliers.__table__.columns.get('company_type')
        assert company_type_column is not None
        assert isinstance(company_type_column.type, Enum)
        assert company_type_column.type.enum_class == CompanyType
        assert company_type_column.nullable is False
        assert company_type_column.unique is None
        assert company_type_column.index is None
        assert company_type_column.default is None

    def test_address_field_properties(self):
        """Test the properties of the address field"""
        address_column = Suppliers.__table__.columns.get('address')
        assert address_column is not None
        assert isinstance(address_column.type, Text)
        assert address_column.nullable is True
        assert address_column.unique is None
        assert address_column.index is None
        assert address_column.default is None

    def test_contact_field_properties(self):
        """Test the properties of the contact field"""
        contact_column = Suppliers.__table__.columns.get('contact')
        assert contact_column is not None
        assert isinstance(contact_column.type, String)
        assert contact_column.type.length == 13
        assert contact_column.nullable is False
        assert contact_column.unique is True
        assert contact_column.index is True
        assert contact_column.default is None

    def test_email_field_properties(self):
        """Test the properties of the email field"""
        email_column = Suppliers.__table__.columns.get('email')
        assert email_column is not None
        assert isinstance(email_column.type, String)
        assert email_column.type.length == 50
        assert email_column.nullable is False
        assert email_column.unique is True
        assert email_column.index is True
        assert email_column.default is None

    def test_relationships_with_other_models(self):
        """Test the relationships with other models"""
        assert_relationship(Suppliers, "products", "supplier")

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_supplier1)
        assert str_repr == "Suppliers(Test Supplier 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        await db_session.refresh(self.test_supplier1, ['products'])
        await db_session.refresh(self.test_supplier2, ['products'])

        assert self.test_supplier1.id == 1
        assert self.test_supplier1.name == "Test Supplier 1"
        assert self.test_supplier1.slug == "test-supplier-1"
        assert self.test_supplier1.company_type == "PT"
        assert self.test_supplier1.address == "Test Address 1"
        assert self.test_supplier1.contact == "081234567890"
        assert self.test_supplier1.email == "test1@example.com"
        assert self.test_supplier1.products == []

        assert self.test_supplier2.id == 2
        assert self.test_supplier2.name == "Test Supplier 2"
        assert self.test_supplier2.slug == "test-supplier-2"
        assert self.test_supplier2.company_type == "CV"
        assert self.test_supplier2.address == "Test Address 2"
        assert self.test_supplier2.contact == "081234567891"
        assert self.test_supplier2.email == "test2@example.com"
        assert self.test_supplier2.products == []

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = Suppliers(
            name="test supplier 3",
            company_type="UD",
            address="test address 3",
            contact="081234567892",
            email="test3@example.com"
        )
        await save_object(db_session, item)

        assert item.id == 3
        assert item.name == "test supplier 3"
        assert item.slug == "test-supplier-3"
        assert item.company_type == "UD"
        assert item.address == "test address 3"
        assert item.contact == "081234567892"
        assert item.email == "test3@example.com"
        assert await count_model_objects(db_session, Suppliers) == 3

        item_with_slug = Suppliers(
            name="test supplier 4",
            slug="slug-supplier-4",
            company_type="INDIVIDUAL",
            address="test address 4",
            contact="081234567893",
            email="test4@example.com"
        )
        await save_object(db_session, item_with_slug)
        assert item_with_slug.id == 4
        assert item_with_slug.name == "test supplier 4"
        # slug should be set to the slugified name
        assert item_with_slug.slug == "test-supplier-4"
        assert item_with_slug.company_type == "INDIVIDUAL"
        assert item_with_slug.address == "test address 4"
        assert item_with_slug.contact == "081234567893"
        assert item_with_slug.email == "test4@example.com"
        assert await count_model_objects(db_session, Suppliers) == 4

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(db_session, Suppliers, self.test_supplier1.id)
        assert item.id == 1
        assert item.name == "Test Supplier 1"
        assert item.slug == "test-supplier-1"
        assert item.company_type == "PT"
        assert item.address == "Test Address 1"
        assert item.contact == "081234567890"
        assert item.email == "test1@example.com"

        item = await get_object_by_id(db_session, Suppliers, self.test_supplier2.id)
        assert item.id == 2
        assert item.name == "Test Supplier 2"
        assert item.slug == "test-supplier-2"
        assert item.company_type == "CV"
        assert item.address == "Test Address 2"
        assert item.contact == "081234567891"
        assert item.email == "test2@example.com"

        items = await get_all_objects(db_session, Suppliers)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].name == "Test Supplier 1"
        assert items[0].slug == "test-supplier-1"
        assert items[0].company_type == "PT"
        assert items[0].address == "Test Address 1"
        assert items[0].contact == "081234567890"
        assert items[0].email == "test1@example.com"

        assert items[1].id == 2
        assert items[1].name == "Test Supplier 2"
        assert items[1].slug == "test-supplier-2"
        assert items[1].company_type == "CV"
        assert items[1].address == "Test Address 2"
        assert items[1].contact == "081234567891"
        assert items[1].email == "test2@example.com"

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(db_session, Suppliers, self.test_supplier1.id)
        item.name = "updated test supplier 1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test supplier 1"
        assert item.slug == "updated-test-supplier-1"
        assert item.company_type == "PT"
        assert item.address == "Test Address 1"
        assert item.contact == "081234567890"
        assert item.email == "test1@example.com"
        assert await count_model_objects(db_session, Suppliers) == 2

        item.slug = "updated-slug-supplier-1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test supplier 1"
        # slug keep the same
        assert item.slug == "updated-test-supplier-1"
        assert item.company_type == "PT"
        assert item.address == "Test Address 1"
        assert item.contact == "081234567890"
        assert item.email == "test1@example.com"
        assert await count_model_objects(db_session, Suppliers) == 2

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_supplier2)

        item = await get_object_by_id(db_session, Suppliers, self.test_supplier2.id)
        assert item is None
        assert await count_model_objects(db_session, Suppliers) == 1

    """
    ================================================
    Validation Tests
    ================================================
    """

    @pytest.mark.asyncio
    async def test_valid_contact_validation(self, db_session: AsyncSession):
        """Test valid contact validation"""
        # Valid numeric contact
        valid_contacts = [
            ("081234567894", "081234567894"),
            ("  081234567895  ", "081234567895")
        ]
        for i, (input_contact, expected_contact) in enumerate(valid_contacts, 1):
            supplier = Suppliers(
                name=f"test contact validation {i}",
                company_type="PT",
                address="test address",
                contact=input_contact,
                email=f"testcontact{i}@example.com"
            )
            await save_object(db_session, supplier)
            assert supplier.contact == expected_contact

    @pytest.mark.asyncio
    async def test_invalid_contact_validation(self, db_session: AsyncSession):
        """Test invalid contact validation"""
        # Contact with non-digit characters should raise ValueError
        invalid_contacts = [
            "081-234-567-896",
            "08123456789a"
        ]
        for i, input_contact in enumerate(invalid_contacts, 1):
            with pytest.raises(ValueError, match="Contact must contain only digits"):
                Suppliers(
                    name=f"test invalid contact {i}",
                    company_type="PT",
                    address="test address",
                    contact=input_contact,
                    email=f"testinvalid{i}@example.com"
                )
            await db_session.rollback()

    @pytest.mark.asyncio
    async def test_valid_email_validation(self, db_session: AsyncSession):
        """Test valid email validation"""
        # Test various valid email formats
        valid_emails = [
            ("test4@example.com", "test4@example.com"),
            ("user.name@domain.co.uk", "user.name@domain.co.uk"),
            ("test+tag@gmail.com", "test+tag@gmail.com"),
            ("user_123@sub.domain.com", "user_123@sub.domain.com"),
            ("TEST5@EXAMPLE.COM", "test5@example.com"),
            # Should be converted to lowercase
            ("  test6@example.com  ", "test6@example.com"),  # Should be trimmed
        ]

        for i, (input_email, expected_email) in enumerate(valid_emails, 1):
            supplier = Suppliers(
                name=f"test email validation {i}",
                company_type="PT",
                address="test address",
                contact=f"0812345678{str(i+10).zfill(2)}",
                email=input_email
            )
            await save_object(db_session, supplier)

            # Verify email was processed correctly
            assert supplier.email == expected_email
            assert '@' in supplier.email

    @pytest.mark.asyncio
    async def test_invalid_email_validation(self, db_session: AsyncSession):
        """Test invalid email validation"""
        # Test invalid email formats
        invalid_emails = [
            "invalid-email",
            "test@",
            "@example.com",
            "",
            "   ",
        ]

        for i, email in enumerate(invalid_emails, 1):
            with pytest.raises(ValueError, match="Invalid email format"):
                Suppliers(
                    name=f"test invalid email {i}",
                    company_type="PT",
                    address="test address",
                    contact=f"0812345678{str(i+10).zfill(2)}",
                    email=email
                )
            await db_session.rollback()

    """
    ================================================
    Relationship Tests (Suppliers -> Products)
    ================================================
    """

    @pytest.fixture
    async def setup_category(self, db_session: AsyncSession, category_factory):
        """Setup category for product tests"""
        self.test_category = await category_factory()

    @pytest.mark.asyncio
    async def test_create_supplier_with_products(
        self, db_session: AsyncSession, setup_category
    ):
        """Test creating supplier with products (valid scenario)"""
        supplier = Suppliers(
            name="Test Supplier with Products",
            company_type="CV",
            contact="098765432112",
            email="supplierwithproducts@test.com",
            products=[
                Products(
                    name="Test Product 1",
                    description="Test Description 1",
                    category_id=self.test_category.id
                ),
                Products(
                    name="Test Product 2",
                    description="Test Description 2",
                    category_id=self.test_category.id
                )
            ]
        )
        await save_object(db_session, supplier)

        retrieved_supplier = await get_object_by_id(
            db_session,
            Suppliers,
            supplier.id
        )
        await db_session.refresh(retrieved_supplier, ['products'])

        assert retrieved_supplier.id == 3
        assert retrieved_supplier.name == "Test Supplier with Products"
        assert len(retrieved_supplier.products) == 2
        assert retrieved_supplier.products[0].name == "Test Product 1"
        assert retrieved_supplier.products[0].category_id == (
            self.test_category.id)
        assert retrieved_supplier.products[0].slug == "test-product-1"
        assert retrieved_supplier.products[0].description == "Test Description 1"

        assert retrieved_supplier.products[1].name == "Test Product 2"
        assert retrieved_supplier.products[1].category_id == (
            self.test_category.id)
        assert retrieved_supplier.products[1].slug == "test-product-2"
        assert retrieved_supplier.products[1].description == "Test Description 2"

    @pytest.mark.asyncio
    async def test_add_multiple_products_to_supplier(
        self, db_session: AsyncSession, setup_category
    ):
        """Test adding multiple products to supplier"""
        for i in range(5):
            product = Products(
                name=f"Test Product {i}",
                description=f"Test Description {i}",
                category_id=self.test_category.id,
                supplier_id=self.test_supplier1.id
            )
            await save_object(db_session, product)

        retrieved_supplier = await get_object_by_id(
            db_session,
            Suppliers,
            self.test_supplier1.id
        )
        await db_session.refresh(retrieved_supplier, ['products'])

        assert len(retrieved_supplier.products) == 5
        for i in range(5):
            assert retrieved_supplier.products[i].id == i + 1
            assert retrieved_supplier.products[i].name == f"Test Product {i}"
            assert retrieved_supplier.products[i].slug == f"test-product-{i}"
            assert retrieved_supplier.products[i].description == f"Test Description {i}"
            assert retrieved_supplier.products[i].category_id == (
                self.test_category.id
            )

    @pytest.mark.asyncio
    async def test_update_suppliers_products(
        self, db_session: AsyncSession, setup_category
    ):
        """Test updating a supplier's products"""
        supplier = await get_object_by_id(
            db_session,
            Suppliers,
            self.test_supplier1.id
        )
        await db_session.refresh(supplier, ['products'])
        assert len(supplier.products) == 0

        supplier.products = [
            Products(name="Test Product 1", category_id=self.test_category.id),
            Products(name="Test Product 2", category_id=self.test_category.id)
        ]
        await save_object(db_session, supplier)
        await db_session.refresh(supplier, ['products'])
        assert len(supplier.products) == 2
        assert supplier.products[0].name == "Test Product 1"
        assert supplier.products[1].name == "Test Product 2"

        supplier.products = [
            Products(name="Test Product 3", category_id=self.test_category.id),
            Products(name="Test Product 4", category_id=self.test_category.id),
            Products(name="Test Product 5", category_id=self.test_category.id)
        ]

        # should fail because test product 1 and test product 2 will lose their
        # supplier_id
        with pytest.raises(IntegrityError):
            await save_object(db_session, supplier)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_supplier_deletion_with_products(
        self, db_session: AsyncSession, setup_category
    ):
        """Test trying to delete supplier with associated products"""
        # Create product associated with the supplier
        product = Products(
            name="Test Product Delete",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier1.id
        )
        await save_object(db_session, product)

        # Try to delete supplier that has associated products
        with pytest.raises(IntegrityError):
            await delete_object(db_session, self.test_supplier1)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_orphaned_product_cleanup(
        self, db_session: AsyncSession, setup_category
    ):
        """Test handling of products when their supplier is deleted"""
        # Create temporary supplier
        temp_supplier = Suppliers(
            name="Temporary Supplier",
            company_type="UD",
            contact="012345678901",
            email="temp@supplier.com"
        )
        await save_object(db_session, temp_supplier)

        # Create product associated with temp supplier
        temp_product = Products(
            name="Temporary Product",
            category_id=self.test_category.id,
            supplier_id=temp_supplier.id
        )
        await save_object(db_session, temp_product)

        # Try to delete the supplier (should fail due to foreign key)
        with pytest.raises(IntegrityError):
            await delete_object(db_session, temp_supplier)
        await db_session.rollback()

        # To properly delete, first remove the product
        await delete_object(db_session, temp_product)

        # Now supplier can be deleted
        await delete_object(db_session, temp_supplier)

        # Verify both are deleted
        deleted_product = await get_object_by_id(
            db_session, Products, temp_product.id
        )
        deleted_supplier = await get_object_by_id(
            db_session, Suppliers, temp_supplier.id
        )

        assert deleted_product is None
        assert deleted_supplier is None

    @pytest.mark.asyncio
    async def test_query_supplier_by_products(
        self, db_session: AsyncSession, setup_category
    ):
        """Test querying supplier by products"""
        # Create products associated with different suppliers
        product1 = Products(
            name="Query Product 1",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier1.id
        )
        await save_object(db_session, product1)

        product2 = Products(
            name="Query Product 2",
            category_id=self.test_category.id,
            supplier_id=self.test_supplier2.id
        )
        await save_object(db_session, product2)

        # Query supplier by products using raw SQL
        stmt = select(Suppliers).join(Products).where(
            Products.name == "Query Product 1"
        )
        result = await db_session.execute(stmt)
        supplier = result.scalar_one_or_none()

        assert supplier.id == self.test_supplier1.id
        assert supplier.name == "Test Supplier 1"
        assert supplier.slug == "test-supplier-1"
