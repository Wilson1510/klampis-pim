from typing import Optional, Literal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import StrictStr, EmailStr
from pydantic_core import PydanticUndefined
import pytest

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema
)
from app.schemas.supplier_schema import (
    SupplierBase, SupplierCreate,
    SupplierUpdate, SupplierInDB,
    SupplierResponse
)
from app.models import Suppliers
from tests.utils.model_test_utils import save_object


class TestSupplierBase:
    """Test cases for the supplier base schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.supplier_dict = {
            "name": "PT Test Supplier",
            "company_type": "PT",
            "address": "Jl. Test No. 123, Jakarta",
            "contact": "081234567890",
            "email": "test@supplier.com"
        }

    def test_supplier_base_schema_inheritance(self):
        """Test that the supplier base schema inherits from BaseSchema"""
        assert issubclass(SupplierBase, BaseSchema)

    def test_supplier_base_fields_inheritance(self):
        """Test that the supplier base schema has correct fields"""
        fields = SupplierBase.model_fields
        assert len(fields) == 5
        assert 'name' in fields
        assert 'company_type' in fields
        assert 'address' in fields
        assert 'contact' in fields
        assert 'email' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        company_type = fields['company_type']
        assert company_type.is_required() is True
        assert company_type.annotation == Literal["INDIVIDUAL", "PT", "CV", "UD"]
        assert company_type.default is PydanticUndefined

        address = fields['address']
        assert address.is_required() is False
        assert address.annotation == Optional[str]
        assert address.default is None

        contact = fields['contact']
        assert contact.is_required() is True
        assert contact.annotation == str
        assert contact.default is PydanticUndefined
        assert contact.metadata[0].min_length == 10
        assert contact.metadata[1].max_length == 13
        assert contact.metadata[2].strict is True

        email = fields['email']
        assert email.is_required() is True
        assert email.annotation == EmailStr
        assert email.default is PydanticUndefined
        assert email.metadata[0].max_length == 50

    def test_supplier_base_schema_input(self):
        schema = SupplierBase(**self.supplier_dict)
        assert schema.name == "PT Test Supplier"
        assert schema.company_type == "PT"
        assert schema.address == "Jl. Test No. 123, Jakarta"
        assert schema.contact == "081234567890"
        assert schema.email == "test@supplier.com"

    def test_supplier_base_schema_input_updated(self):
        schema = SupplierBase(**self.supplier_dict)
        assert schema.name == "PT Test Supplier"
        assert schema.company_type == "PT"
        assert schema.address == "Jl. Test No. 123, Jakarta"
        assert schema.contact == "081234567890"
        assert schema.email == "test@supplier.com"

        schema.name = "PT Test Supplier Updated"
        assert schema.name == "PT Test Supplier Updated"

    def test_supplier_base_schema_model_dump(self):
        schema = SupplierBase(**self.supplier_dict)
        assert schema.model_dump() == {
            "name": "PT Test Supplier",
            "company_type": "PT",
            "address": "Jl. Test No. 123, Jakarta",
            "contact": "081234567890",
            "email": "test@supplier.com"
        }

    def test_supplier_base_schema_model_dump_json(self):
        schema = SupplierBase(**self.supplier_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"PT Test Supplier",'\
            '"company_type":"PT",'\
            '"address":"Jl. Test No. 123, Jakarta",'\
            '"contact":"081234567890",'\
            '"email":"test@supplier.com"'\
            '}'

    def test_supplier_base_contact_validation_invalid_chars(self):
        """Test contact validation with invalid characters"""
        invalid_dict = self.supplier_dict.copy()
        invalid_dict["contact"] = "081-234-567"

        with pytest.raises(ValueError, match="Contact must contain only digits"):
            SupplierBase(**invalid_dict)


class TestSupplierCreate:
    """Test cases for the supplier create schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.supplier_dict = {
            "name": "CV Test Supplier",
            "company_type": "CV",
            "address": "Jl. Create No. 456, Bandung",
            "contact": "0227654321",
            "email": "create@supplier.com"
        }

    def test_supplier_create_schema_inheritance(self):
        """Test that the supplier create schema inherits from BaseCreateSchema"""
        assert issubclass(SupplierCreate, BaseCreateSchema)
        assert issubclass(SupplierCreate, SupplierBase)

    def test_supplier_create_fields_inheritance(self):
        """Test that the supplier create schema has correct fields"""
        fields = SupplierCreate.model_fields
        assert len(fields) == 7  # 5 base + 2 from BaseCreateSchema
        assert 'name' in fields
        assert 'company_type' in fields
        assert 'address' in fields
        assert 'contact' in fields
        assert 'email' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        company_type = fields['company_type']
        assert company_type.is_required() is True
        assert company_type.annotation == Literal["INDIVIDUAL", "PT", "CV", "UD"]
        assert company_type.default is PydanticUndefined

        address = fields['address']
        assert address.is_required() is False
        assert address.annotation == Optional[str]
        assert address.default is None

        contact = fields['contact']
        assert contact.is_required() is True
        assert contact.annotation == str
        assert contact.default is PydanticUndefined
        assert contact.metadata[0].min_length == 10
        assert contact.metadata[1].max_length == 13
        assert contact.metadata[2].strict is True

        email = fields['email']
        assert email.is_required() is True
        assert email.annotation == EmailStr
        assert email.default is PydanticUndefined
        assert email.metadata[0].max_length == 50

    def test_supplier_create_schema_input(self):
        schema = SupplierCreate(**self.supplier_dict)
        assert schema.name == "CV Test Supplier"
        assert schema.company_type == "CV"
        assert schema.address == "Jl. Create No. 456, Bandung"
        assert schema.contact == "0227654321"
        assert schema.email == "create@supplier.com"

    def test_supplier_create_schema_input_updated(self):
        schema = SupplierCreate(**self.supplier_dict)
        assert schema.name == "CV Test Supplier"
        assert schema.company_type == "CV"
        assert schema.address == "Jl. Create No. 456, Bandung"
        assert schema.contact == "0227654321"
        assert schema.email == "create@supplier.com"

        schema.name = "CV Test Supplier Updated"
        assert schema.name == "CV Test Supplier Updated"

    def test_supplier_create_schema_model_dump(self):
        schema = SupplierCreate(**self.supplier_dict)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "name": "CV Test Supplier",
            "company_type": "CV",
            "address": "Jl. Create No. 456, Bandung",
            "contact": "0227654321",
            "email": "create@supplier.com"
        }

    def test_supplier_create_schema_model_dump_json(self):
        schema = SupplierCreate(**self.supplier_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"name":"CV Test Supplier",'\
            '"company_type":"CV",'\
            '"address":"Jl. Create No. 456, Bandung",'\
            '"contact":"0227654321",'\
            '"email":"create@supplier.com"'\
            '}'


class TestSupplierUpdate:
    """Test cases for the supplier update schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.supplier_dict = {
            "name": "UD Test Supplier",
            "company_type": "UD",
            "address": "Jl. Update No. 789, Surabaya",
            "contact": "0318765432",
            "email": "update@supplier.com"
        }

    def test_supplier_update_schema_inheritance(self):
        """Test that the supplier update schema inherits from BaseUpdateSchema"""
        assert issubclass(SupplierUpdate, BaseUpdateSchema)
        assert issubclass(SupplierUpdate, SupplierBase)

    def test_supplier_update_fields_inheritance(self):
        """Test that the supplier update schema has correct fields"""
        fields = SupplierUpdate.model_fields
        assert len(fields) == 7  # 5 base + 2 from BaseUpdateSchema
        assert 'name' in fields
        assert 'company_type' in fields
        assert 'address' in fields
        assert 'contact' in fields
        assert 'email' in fields

        name = fields['name']
        assert name.is_required() is False
        assert name.annotation == Optional[StrictStr]
        assert name.default is None
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100

        company_type = fields['company_type']
        assert company_type.is_required() is False
        assert company_type.annotation == Optional[
            Literal["INDIVIDUAL", "PT", "CV", "UD"]
        ]
        assert company_type.default is None

        address = fields['address']
        assert address.is_required() is False
        assert address.annotation == Optional[str]
        assert address.default is None

        contact = fields['contact']
        assert contact.is_required() is False
        assert contact.annotation == Optional[StrictStr]
        assert contact.default is None
        assert contact.metadata[0].min_length == 10
        assert contact.metadata[1].max_length == 13

        email = fields['email']
        assert email.is_required() is False
        assert email.annotation == Optional[EmailStr]
        assert email.default is None
        assert email.metadata[0].max_length == 50

    def test_supplier_update_schema_input(self):
        schema = SupplierUpdate(**self.supplier_dict)
        assert schema.name == "UD Test Supplier"
        assert schema.company_type == "UD"
        assert schema.address == "Jl. Update No. 789, Surabaya"
        assert schema.contact == "0318765432"
        assert schema.email == "update@supplier.com"

    def test_supplier_update_schema_input_updated(self):
        schema = SupplierUpdate(**self.supplier_dict)
        assert schema.name == "UD Test Supplier"
        assert schema.company_type == "UD"
        assert schema.address == "Jl. Update No. 789, Surabaya"
        assert schema.contact == "0318765432"
        assert schema.email == "update@supplier.com"

        schema.name = "UD Test Supplier Updated"
        assert schema.name == "UD Test Supplier Updated"

    def test_supplier_update_schema_model_dump(self):
        schema = SupplierUpdate(**self.supplier_dict)
        assert schema.model_dump() == {
            "is_active": None,
            "sequence": None,
            "name": "UD Test Supplier",
            "company_type": "UD",
            "address": "Jl. Update No. 789, Surabaya",
            "contact": "0318765432",
            "email": "update@supplier.com"
        }

    def test_supplier_update_schema_model_dump_json(self):
        schema = SupplierUpdate(**self.supplier_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":null,'\
            '"sequence":null,'\
            '"name":"UD Test Supplier",'\
            '"company_type":"UD",'\
            '"address":"Jl. Update No. 789, Surabaya",'\
            '"contact":"0318765432",'\
            '"email":"update@supplier.com"'\
            '}'

    def test_supplier_update_contact_validation_optional(self):
        """Test contact validation in update schema with invalid contact"""
        invalid_dict = {"contact": "081-234-567"}

        with pytest.raises(ValueError, match="Contact must contain only digits"):
            SupplierUpdate(**invalid_dict)


class TestSupplierInDB:
    """Test cases for the supplier in db schema"""

    def test_supplier_in_db_inheritance(self):
        """Test that the supplier in db schema inherits from BaseInDB"""
        assert issubclass(SupplierInDB, BaseInDB)
        assert issubclass(SupplierInDB, SupplierBase)

    def test_supplier_in_db_fields_inheritance(self):
        """Test that the supplier in db schema has correct fields"""
        fields = SupplierInDB.model_fields
        assert len(fields) == 13  # 5 base + 8 from BaseInDB
        assert 'name' in fields
        assert 'company_type' in fields
        assert 'address' in fields
        assert 'contact' in fields
        assert 'email' in fields
        assert 'slug' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        company_type = fields['company_type']
        assert company_type.is_required() is True
        assert company_type.annotation == Literal["INDIVIDUAL", "PT", "CV", "UD"]
        assert company_type.default is PydanticUndefined

        address = fields['address']
        assert address.is_required() is False
        assert address.annotation == Optional[str]
        assert address.default is None

        contact = fields['contact']
        assert contact.is_required() is True
        assert contact.annotation == str
        assert contact.default is PydanticUndefined
        assert contact.metadata[0].min_length == 10
        assert contact.metadata[1].max_length == 13
        assert contact.metadata[2].strict is True

        email = fields['email']
        assert email.is_required() is True
        assert email.annotation == EmailStr
        assert email.default is PydanticUndefined

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        model_config = SupplierInDB.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_supplier_in_db_model_validate(self, db_session: AsyncSession):
        """Test that the supplier in db schema model validate"""
        model = Suppliers(
            name="Test Supplier InDB",
            company_type="INDIVIDUAL",
            address="Jl. InDB No. 999, Yogyakarta",
            contact="0274123456",
            email="indb@supplier.com"
        )
        await save_object(db_session, model)

        query = select(Suppliers).where(Suppliers.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = SupplierInDB.model_validate(db_model)
        assert db_schema_object == SupplierInDB(
            id=model.id,
            name="Test Supplier InDB",
            company_type="INDIVIDUAL",
            address="Jl. InDB No. 999, Yogyakarta",
            contact="0274123456",
            email="indb@supplier.com",
            slug="test-supplier-indb",
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )

    @pytest.mark.asyncio
    async def test_supplier_in_db_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the supplier in db schema model validate updated"""
        model = Suppliers(
            name="Test Supplier InDB",
            company_type="INDIVIDUAL",
            address="Jl. InDB No. 999, Yogyakarta",
            contact="0274123456",
            email="indb@supplier.com"
        )
        await save_object(db_session, model)

        query = select(Suppliers).where(Suppliers.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Test Supplier InDB Updated"
        db_model.address = "Jl. InDB Updated No. 999, Yogyakarta"

        db_schema_object = SupplierInDB.model_validate(db_model)
        assert db_schema_object == SupplierInDB(
            id=model.id,
            name="Test Supplier InDB Updated",
            company_type="INDIVIDUAL",
            address="Jl. InDB Updated No. 999, Yogyakarta",
            contact="0274123456",
            email="indb@supplier.com",
            slug="test-supplier-indb-updated",
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )


class TestSupplierResponse:
    """Test cases for the supplier response schema"""

    def test_supplier_response_inheritance(self):
        """Test that the supplier response schema inherits from SupplierInDB"""
        assert issubclass(SupplierResponse, SupplierInDB)

    def test_supplier_response_fields_inheritance(self):
        """Test that the supplier response schema has correct fields"""
        fields = SupplierResponse.model_fields
        assert len(fields) == 13  # Same as SupplierInDB
        assert 'name' in fields
        assert 'company_type' in fields
        assert 'address' in fields
        assert 'contact' in fields
        assert 'email' in fields
        assert 'slug' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        company_type = fields['company_type']
        assert company_type.is_required() is True
        assert company_type.annotation == Literal["INDIVIDUAL", "PT", "CV", "UD"]
        assert company_type.default is PydanticUndefined

        address = fields['address']
        assert address.is_required() is False
        assert address.annotation == Optional[str]
        assert address.default is None

        contact = fields['contact']
        assert contact.is_required() is True
        assert contact.annotation == str
        assert contact.default is PydanticUndefined
        assert contact.metadata[0].min_length == 10
        assert contact.metadata[1].max_length == 13
        assert contact.metadata[2].strict is True

        email = fields['email']
        assert email.is_required() is True
        assert email.annotation == EmailStr
        assert email.default is PydanticUndefined

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        model_config = SupplierResponse.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_supplier_response_model_validate(self, db_session: AsyncSession):
        """Test that the supplier response schema model validate"""
        model = Suppliers(
            name="Test Supplier Response",
            company_type="PT",
            address="Jl. Response No. 888, Medan",
            contact="0617654321",
            email="response@supplier.com"
        )
        await save_object(db_session, model)

        query = select(Suppliers).where(Suppliers.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = SupplierResponse.model_validate(db_model)

        assert db_schema_object == SupplierResponse(
            id=model.id,
            name="Test Supplier Response",
            company_type="PT",
            address="Jl. Response No. 888, Medan",
            contact="0617654321",
            email="response@supplier.com",
            slug="test-supplier-response",
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )

    @pytest.mark.asyncio
    async def test_supplier_response_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the supplier response schema model validate updated"""
        model = Suppliers(
            name="Test Supplier Response",
            company_type="PT",
            address="Jl. Response No. 888, Medan",
            contact="0617654321",
            email="response@supplier.com"
        )
        await save_object(db_session, model)

        query = select(Suppliers).where(Suppliers.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Test Supplier Response Updated"
        db_model.company_type = "CV"
        db_model.address = "Jl. Response Updated No. 888, Medan"

        db_schema_object = SupplierResponse.model_validate(db_model)
        assert db_schema_object == SupplierResponse(
            id=model.id,
            name="Test Supplier Response Updated",
            company_type="CV",
            address="Jl. Response Updated No. 888, Medan",
            contact="0617654321",
            email="response@supplier.com",
            slug="test-supplier-response-updated",
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )
