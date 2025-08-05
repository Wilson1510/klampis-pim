from typing import Optional, Literal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import StrictStr
from pydantic_core import PydanticUndefined
import pytest

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema
)
from app.schemas.attribute_schema import (
    AttributeBase, AttributeCreate,
    AttributeUpdate, AttributeInDB,
    AttributeResponse
)
from app.models import Attributes
from tests.utils.model_test_utils import save_object


class TestAttributeBase:
    """Test cases for the attribute base schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.attribute_dict = {
            "name": "Volume",
            "data_type": "NUMBER",
            "uom": "ml"
        }

    def test_attribute_base_schema_inheritance(self):
        """Test that the attribute base schema inherits from BaseSchema"""
        assert issubclass(AttributeBase, BaseSchema)

    def test_attribute_base_fields_inheritance(self):
        """Test that the attribute base schema has correct fields"""
        fields = AttributeBase.model_fields
        assert len(fields) == 3
        assert 'name' in fields
        assert 'data_type' in fields
        assert 'uom' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        data_type = fields['data_type']
        assert data_type.is_required() is False
        assert data_type.annotation == Literal["TEXT", "NUMBER", "BOOLEAN", "DATE"]
        assert data_type.default == "TEXT"

        uom = fields['uom']
        assert uom.is_required() is False
        assert uom.annotation == Optional[StrictStr]
        assert uom.default is None
        assert uom.metadata[0].max_length == 15

    def test_attribute_base_schema_input(self):
        schema = AttributeBase(**self.attribute_dict)
        assert schema.name == "Volume"
        assert schema.data_type == "NUMBER"
        assert schema.uom == "ml"

    def test_attribute_base_schema_input_updated(self):
        schema = AttributeBase(**self.attribute_dict)
        assert schema.name == "Volume"
        assert schema.data_type == "NUMBER"
        assert schema.uom == "ml"

        schema.name = "Volume Updated"
        assert schema.name == "Volume Updated"

    def test_attribute_base_schema_model_dump(self):
        schema = AttributeBase(**self.attribute_dict)
        assert schema.model_dump() == {
            "name": "Volume",
            "data_type": "NUMBER",
            "uom": "ml"
        }

    def test_attribute_base_schema_model_dump_json(self):
        schema = AttributeBase(**self.attribute_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"Volume",'\
            '"data_type":"NUMBER",'\
            '"uom":"ml"'\
            '}'


class TestAttributeCreate:
    """Test cases for the attribute create schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.attribute_dict = {
            "name": "Flavor",
            "uom": None
        }

    def test_attribute_create_schema_inheritance(self):
        """Test that the attribute create schema inherits from BaseCreateSchema"""
        assert issubclass(AttributeCreate, BaseCreateSchema)
        assert issubclass(AttributeCreate, AttributeBase)

    def test_attribute_create_fields_inheritance(self):
        """Test that the attribute create schema has correct fields"""
        fields = AttributeCreate.model_fields
        assert len(fields) == 7  # 3 base + 4 from BaseCreateSchema
        assert 'name' in fields
        assert 'data_type' in fields
        assert 'uom' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        data_type = fields['data_type']
        assert data_type.is_required() is False
        assert data_type.annotation == Literal["TEXT", "NUMBER", "BOOLEAN", "DATE"]
        assert data_type.default == "TEXT"

        uom = fields['uom']
        assert uom.is_required() is False
        assert uom.annotation == Optional[StrictStr]
        assert uom.default is None
        assert uom.metadata[0].max_length == 15

    def test_attribute_create_schema_input(self):
        schema = AttributeCreate(**self.attribute_dict)
        assert schema.name == "Flavor"
        assert schema.data_type == "TEXT"
        assert schema.uom is None

    def test_attribute_create_schema_input_updated(self):
        schema = AttributeCreate(**self.attribute_dict)
        assert schema.name == "Flavor"
        assert schema.data_type == "TEXT"
        assert schema.uom is None

        schema.name = "Flavor Updated"
        assert schema.name == "Flavor Updated"

    def test_attribute_create_schema_model_dump(self):
        schema = AttributeCreate(**self.attribute_dict)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "created_by": 1,
            "updated_by": 1,
            "name": "Flavor",
            "data_type": "TEXT",
            "uom": None
        }

    def test_attribute_create_schema_model_dump_json(self):
        schema = AttributeCreate(**self.attribute_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"created_by":1,'\
            '"updated_by":1,'\
            '"name":"Flavor",'\
            '"data_type":"TEXT",'\
            '"uom":null'\
            '}'


class TestAttributeUpdate:
    """Test cases for the attribute update schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.attribute_dict = {
            "name": "Weight",
            "data_type": "NUMBER",
            "uom": "kg"
        }

    def test_attribute_update_schema_inheritance(self):
        """Test that the attribute update schema inherits from BaseUpdateSchema"""
        assert issubclass(AttributeUpdate, BaseUpdateSchema)
        assert issubclass(AttributeUpdate, AttributeBase)

    def test_attribute_update_fields_inheritance(self):
        """Test that the attribute update schema has correct fields"""
        fields = AttributeUpdate.model_fields
        assert len(fields) == 6  # 3 base + 3 from BaseUpdateSchema
        assert 'name' in fields
        assert 'data_type' in fields
        assert 'uom' in fields

        name = fields['name']
        assert name.is_required() is False
        assert name.annotation == Optional[StrictStr]
        assert name.default is None
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50

        data_type = fields['data_type']
        assert data_type.is_required() is False
        assert data_type.annotation == Optional[
            Literal["TEXT", "NUMBER", "BOOLEAN", "DATE"]
        ]
        assert data_type.default is None

        uom = fields['uom']
        assert uom.is_required() is False
        assert uom.annotation == Optional[StrictStr]
        assert uom.default is None
        assert uom.metadata[0].max_length == 15

    def test_attribute_update_schema_input(self):
        schema = AttributeUpdate(**self.attribute_dict)
        assert schema.name == "Weight"
        assert schema.data_type == "NUMBER"
        assert schema.uom == "kg"

    def test_attribute_update_schema_input_updated(self):
        schema = AttributeUpdate(**self.attribute_dict)
        assert schema.name == "Weight"
        assert schema.data_type == "NUMBER"
        assert schema.uom == "kg"

        schema.name = "Weight Updated"
        assert schema.name == "Weight Updated"

    def test_attribute_update_schema_model_dump(self):
        schema = AttributeUpdate(**self.attribute_dict)
        assert schema.model_dump() == {
            "is_active": None,
            "sequence": None,
            "updated_by": None,
            "name": "Weight",
            "data_type": "NUMBER",
            "uom": "kg"
        }

    def test_attribute_update_schema_model_dump_json(self):
        schema = AttributeUpdate(**self.attribute_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":null,'\
            '"sequence":null,'\
            '"updated_by":null,'\
            '"name":"Weight",'\
            '"data_type":"NUMBER",'\
            '"uom":"kg"'\
            '}'


class TestAttributeInDB:
    """Test cases for the attribute in db schema"""

    def test_attribute_in_db_inheritance(self):
        """Test that the attribute in db schema inherits from BaseInDB"""
        assert issubclass(AttributeInDB, BaseInDB)
        assert issubclass(AttributeInDB, AttributeBase)

    def test_attribute_in_db_fields_inheritance(self):
        """Test that the attribute in db schema has correct fields"""
        fields = AttributeInDB.model_fields
        assert len(fields) == 11  # 3 base + 1 code + 7 from BaseInDB
        assert 'name' in fields
        assert 'data_type' in fields
        assert 'uom' in fields
        assert 'code' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        data_type = fields['data_type']
        assert data_type.is_required() is False
        assert data_type.annotation == Literal["TEXT", "NUMBER", "BOOLEAN", "DATE"]
        assert data_type.default == "TEXT"

        uom = fields['uom']
        assert uom.is_required() is False
        assert uom.annotation == Optional[StrictStr]
        assert uom.default is None
        assert uom.metadata[0].max_length == 15

        code = fields['code']
        assert code.is_required() is True
        assert code.annotation == str
        assert code.default is PydanticUndefined

        model_config = AttributeInDB.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_attribute_in_db_model_validate(self, db_session: AsyncSession):
        """Test that the attribute in db schema model validate"""
        model = Attributes(
            name="Test Attribute InDB",
            data_type="BOOLEAN",
            uom=None
        )
        await save_object(db_session, model)

        query = select(Attributes).where(Attributes.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = AttributeInDB.model_validate(db_model)
        assert db_schema_object == AttributeInDB(
            id=model.id,
            name="Test Attribute InDB",
            data_type="BOOLEAN",
            uom=None,
            code="TEST-ATTRIBUTE-INDB",
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )

    @pytest.mark.asyncio
    async def test_attribute_in_db_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the attribute in db schema model validate updated"""
        model = Attributes(
            name="Test Attribute InDB",
            data_type="BOOLEAN",
            uom=None
        )
        await save_object(db_session, model)

        query = select(Attributes).where(Attributes.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Test Attribute InDB Updated"
        db_model.data_type = "DATE"
        db_model.uom = "days"

        db_schema_object = AttributeInDB.model_validate(db_model)
        assert db_schema_object == AttributeInDB(
            id=model.id,
            name="Test Attribute InDB Updated",
            data_type="DATE",
            uom="days",
            code="TEST-ATTRIBUTE-INDB-UPDATED",
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )


class TestAttributeResponse:
    """Test cases for the attribute response schema"""

    def test_attribute_response_inheritance(self):
        """Test that the attribute response schema inherits from AttributeInDB"""
        assert issubclass(AttributeResponse, AttributeInDB)

    def test_attribute_response_fields_inheritance(self):
        """Test that the attribute response schema has correct fields"""
        fields = AttributeResponse.model_fields
        assert len(fields) == 11  # Same as AttributeInDB
        assert 'name' in fields
        assert 'data_type' in fields
        assert 'uom' in fields
        assert 'code' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        data_type = fields['data_type']
        assert data_type.is_required() is False
        assert data_type.annotation == Literal["TEXT", "NUMBER", "BOOLEAN", "DATE"]
        assert data_type.default == "TEXT"

        uom = fields['uom']
        assert uom.is_required() is False
        assert uom.annotation == Optional[StrictStr]
        assert uom.default is None
        assert uom.metadata[0].max_length == 15

        code = fields['code']
        assert code.is_required() is True
        assert code.annotation == str
        assert code.default is PydanticUndefined

        model_config = AttributeResponse.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_attribute_response_model_validate(self, db_session: AsyncSession):
        """Test that the attribute response schema model validate"""
        model = Attributes(
            name="Test Attribute Response",
            data_type="NUMBER",
            uom="cm"
        )
        await save_object(db_session, model)

        query = select(Attributes).where(Attributes.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = AttributeResponse.model_validate(db_model)

        assert db_schema_object == AttributeResponse(
            id=model.id,
            name="Test Attribute Response",
            data_type="NUMBER",
            uom="cm",
            code="TEST-ATTRIBUTE-RESPONSE",
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )

    @pytest.mark.asyncio
    async def test_attribute_response_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the attribute response schema model validate updated"""
        model = Attributes(
            name="Test Attribute Response",
            data_type="NUMBER",
            uom="cm"
        )
        await save_object(db_session, model)

        query = select(Attributes).where(Attributes.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Test Attribute Response Updated"
        db_model.data_type = "TEXT"
        db_model.uom = None

        db_schema_object = AttributeResponse.model_validate(db_model)
        assert db_schema_object == AttributeResponse(
            id=model.id,
            name="Test Attribute Response Updated",
            data_type="TEXT",
            uom=None,
            code="TEST-ATTRIBUTE-RESPONSE-UPDATED",
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )
