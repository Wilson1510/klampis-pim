from sqlalchemy import String, event, Text, Integer, CheckConstraint
from sqlalchemy.exc import IntegrityError
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
    assert_relationship,
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
        assert str_repr == "Suppliers(name=test supplier 1, slug=test-supplier-1)"
