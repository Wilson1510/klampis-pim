from sqlalchemy import String, Text, event
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from app.models.supplier_model import Suppliers
from app.core.listeners import _set_slug
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    count_model_objects
)


class TestSupplier:
    """Test suite for Supplier model and relationships"""
    @pytest.fixture(autouse=True)
    async def setup_objects(self, db_session: AsyncSession):
        """Setup method for the test suite"""
        # Create supplier
        self.test_supplier1 = Suppliers(
            name="test supplier 1",
            company_type="PT",
            address="test address 1",
            contact="081234567890",
            email="test1@example.com"
        )
        await save_object(db_session, self.test_supplier1)

        self.test_supplier2 = Suppliers(
            name="test supplier 2",
            company_type="CV",
            address="test address 2",
            contact="081234567891",
            email="test2@example.com"
        )

        await save_object(db_session, self.test_supplier2)

    def test_inheritance_from_base_model(self):
        """Test that Supplier model inherits from Base model"""
        assert issubclass(Suppliers, Base)

    def test_fields_with_validation(self):
        """Test that the fields have the expected validation"""
        assert hasattr(Suppliers, 'validate_contact')
        assert hasattr(Suppliers, 'validate_email')
        assert hasattr(Suppliers, 'validate_company_type')
        assert not hasattr(Suppliers, 'validate_name')

        assert 'contact' in Suppliers.__mapper__.validators
        assert 'email' in Suppliers.__mapper__.validators
        assert 'company_type' in Suppliers.__mapper__.validators
        assert 'name' not in Suppliers.__mapper__.validators

        assert len(Suppliers.__mapper__.validators) == 3

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
        assert isinstance(company_type_column.type, String)
        assert company_type_column.type.length == 50
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

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_supplier1)
        assert str_repr == "Suppliers(test supplier 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        assert self.test_supplier1.id == 1
        assert self.test_supplier1.name == "test supplier 1"
        assert self.test_supplier1.slug == "test-supplier-1"
        assert self.test_supplier1.company_type == "PT"
        assert self.test_supplier1.address == "test address 1"
        assert self.test_supplier1.contact == "081234567890"
        assert self.test_supplier1.email == "test1@example.com"

        assert self.test_supplier2.id == 2
        assert self.test_supplier2.name == "test supplier 2"
        assert self.test_supplier2.slug == "test-supplier-2"
        assert self.test_supplier2.company_type == "CV"
        assert self.test_supplier2.address == "test address 2"
        assert self.test_supplier2.contact == "081234567891"
        assert self.test_supplier2.email == "test2@example.com"

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
        assert item.name == "test supplier 1"
        assert item.slug == "test-supplier-1"
        assert item.company_type == "PT"
        assert item.address == "test address 1"
        assert item.contact == "081234567890"
        assert item.email == "test1@example.com"

        item = await get_object_by_id(db_session, Suppliers, self.test_supplier2.id)
        assert item.id == 2
        assert item.name == "test supplier 2"
        assert item.slug == "test-supplier-2"
        assert item.company_type == "CV"
        assert item.address == "test address 2"
        assert item.contact == "081234567891"
        assert item.email == "test2@example.com"

        items = await get_all_objects(db_session, Suppliers)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].name == "test supplier 1"
        assert items[0].slug == "test-supplier-1"
        assert items[0].company_type == "PT"
        assert items[0].address == "test address 1"
        assert items[0].contact == "081234567890"
        assert items[0].email == "test1@example.com"

        assert items[1].id == 2
        assert items[1].name == "test supplier 2"
        assert items[1].slug == "test-supplier-2"
        assert items[1].company_type == "CV"
        assert items[1].address == "test address 2"
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
        assert item.address == "test address 1"
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
        assert item.address == "test address 1"
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

    # Validation Tests

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

    @pytest.mark.asyncio
    async def test_valid_company_type_validation(self, db_session: AsyncSession):
        """Test valid company_type validation"""
        valid_types = ["INDIVIDUAL", "PT", "CV", "UD"]

        for i, company_type in enumerate(valid_types):
            supplier = Suppliers(
                name=f"test company type {company_type.lower()}",
                company_type=company_type.lower(),  # Test lowercase input
                address="test address",
                contact=f"0812345678{str(i+10).zfill(2)}",
                email=f"test{company_type.lower()}@example.com"
            )
            await save_object(db_session, supplier)
            # Company type should be uppercased and trimmed
            assert supplier.company_type == company_type

        # Test with spaces
        supplier_with_spaces = Suppliers(
            name="test company type with spaces",
            company_type="  pt  ",
            address="test address",
            contact="081234567814",
            email="testspaces@example.com"
        )
        await save_object(db_session, supplier_with_spaces)
        assert supplier_with_spaces.company_type == "PT"

    @pytest.mark.asyncio
    async def test_invalid_company_type_validation(self, db_session: AsyncSession):
        """Test invalid company_type validation"""
        # Invalid company type should raise ValueError
        invalid_types = ["LLC", "CORP", "123", "&^%$", ""]
        for i, company_type in enumerate(invalid_types):
            with pytest.raises(ValueError, match="Invalid company type"):
                Suppliers(
                    name=f"test invalid company type {i}",
                    company_type=company_type,
                    address="test address",
                    contact=f"0812345678{str(i+10).zfill(2)}",
                    email=f"testinvalid{i}@example.com"
                )
            await db_session.rollback()
