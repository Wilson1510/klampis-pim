from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import StrictStr
from pydantic_core import PydanticUndefined
import pytest

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema
)
from app.schemas.pricelist_schema import (
    PricelistBase, PricelistCreate,
    PricelistUpdate, PricelistInDB,
    PricelistResponse
)
from app.models import Pricelists
from tests.utils.model_test_utils import save_object, get_object_by_id


class TestPricelistBase:
    """Test cases for the pricelist base schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.pricelist_dict = {"name": "Test Pricelist"}

    def test_pricelist_base_schema_inheritance(self):
        """Test that the pricelist base schema inherits from BaseSchema"""
        assert issubclass(PricelistBase, BaseSchema)

    def test_pricelist_base_fields_inheritance(self):
        """Test that the pricelist base schema inherits from BaseSchema"""
        fields = PricelistBase.model_fields
        assert len(fields) == 2
        assert 'name' in fields
        assert 'description' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        description = fields['description']
        assert description.is_required() is False
        assert description.annotation == Optional[str]
        assert description.default is None

    def test_pricelist_base_schema_input(self):
        schema = PricelistBase(**self.pricelist_dict)
        assert schema.name == "Test Pricelist"

    def test_pricelist_base_schema_input_updated(self):
        schema = PricelistBase(**self.pricelist_dict)
        assert schema.name == "Test Pricelist"

        schema.name = "Test Pricelist Updated"
        assert schema.name == "Test Pricelist Updated"

    def test_pricelist_base_schema_model_dump(self):
        schema = PricelistBase(**self.pricelist_dict)
        assert schema.model_dump() == {
            "name": "Test Pricelist",
            "description": None
        }

    def test_pricelist_base_schema_model_dump_json(self):
        schema = PricelistBase(**self.pricelist_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"Test Pricelist",'\
            '"description":null'\
            '}'


class TestPricelistCreate:
    """Test cases for the pricelist schema create"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.pricelist_dict = {"name": "Test Pricelist"}

    def test_pricelist_create_schema_inheritance(self):
        """Test that the pricelist create schema inherits from BaseCreateSchema"""
        assert issubclass(PricelistCreate, BaseCreateSchema)
        assert issubclass(PricelistCreate, PricelistBase)

    def test_pricelist_create_fields_inheritance(self):
        """Test that the pricelist create schema inherits from BaseCreateSchema"""
        fields = PricelistCreate.model_fields
        assert len(fields) == 6
        assert 'name' in fields
        assert 'description' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        description = fields['description']
        assert description.is_required() is False
        assert description.annotation == Optional[str]
        assert description.default is None

    def test_pricelist_create_schema_input(self):
        schema = PricelistCreate(**self.pricelist_dict)
        assert schema.name == "Test Pricelist"

    def test_pricelist_create_schema_input_updated(self):
        schema = PricelistCreate(**self.pricelist_dict)
        assert schema.name == "Test Pricelist"

        schema.name = "Test Pricelist Updated"
        assert schema.name == "Test Pricelist Updated"

    def test_pricelist_create_schema_model_dump(self):
        schema = PricelistCreate(**self.pricelist_dict)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "created_by": 1,
            "updated_by": 1,
            "name": "Test Pricelist",
            "description": None
        }

    def test_pricelist_create_schema_model_dump_json(self):
        schema = PricelistCreate(**self.pricelist_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"created_by":1,'\
            '"updated_by":1,'\
            '"name":"Test Pricelist",'\
            '"description":null'\
            '}'


class TestPricelistUpdate:
    """Test cases for the pricelist schema update"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.pricelist_dict = {"name": "Test Pricelist"}

    def test_pricelist_update_schema_inheritance(self):
        """Test that the pricelist update schema inherits from BaseUpdateSchema"""
        assert issubclass(PricelistUpdate, BaseUpdateSchema)
        assert issubclass(PricelistUpdate, PricelistBase)

    def test_pricelist_update_fields_inheritance(self):
        """Test that the pricelist update schema inherits from BaseUpdateSchema"""
        fields = PricelistUpdate.model_fields
        assert len(fields) == 5
        assert 'name' in fields
        assert 'description' in fields

        name = fields['name']
        assert name.is_required() is False
        assert name.annotation == Optional[StrictStr]
        assert name.default is None
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50

        description = fields['description']
        assert description.is_required() is False
        assert description.annotation == Optional[str]
        assert description.default is None

    def test_pricelist_update_schema_input(self):
        schema = PricelistUpdate(**self.pricelist_dict)
        assert schema.name == "Test Pricelist"

    def test_pricelist_update_schema_input_updated(self):
        schema = PricelistUpdate(**self.pricelist_dict)
        assert schema.name == "Test Pricelist"

        schema.name = "Test Pricelist Updated"
        assert schema.name == "Test Pricelist Updated"

    def test_pricelist_update_schema_model_dump(self):
        schema = PricelistUpdate(**self.pricelist_dict)
        assert schema.model_dump() == {
            "is_active": None,
            "sequence": None,
            "updated_by": None,
            "name": "Test Pricelist",
            "description": None
        }

    def test_pricelist_update_schema_model_dump_json(self):
        schema = PricelistUpdate(**self.pricelist_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":null,'\
            '"sequence":null,'\
            '"updated_by":null,'\
            '"name":"Test Pricelist",'\
            '"description":null'\
            '}'


class TestPricelistInDB:
    """Test cases for the pricelist schema in db"""

    def test_pricelist_in_db_inheritance(self):
        """Test that the pricelist schema in db inherits from BaseInDB"""
        assert issubclass(PricelistInDB, BaseInDB)
        assert issubclass(PricelistInDB, PricelistBase)

    def test_pricelist_in_db_fields_inheritance(self):
        """Test that the pricelist schema in db inherits from BaseInDB"""
        fields = PricelistInDB.model_fields
        assert len(fields) == 10
        assert 'name' in fields
        assert 'description' in fields
        assert 'code' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        description = fields['description']
        assert description.is_required() is False
        assert description.annotation == Optional[str]
        assert description.default is None

        code = fields['code']
        assert code.is_required() is True
        assert code.annotation == str
        assert code.default is PydanticUndefined

        model_config = PricelistInDB.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_pricelist_in_db_model_validate(self, db_session: AsyncSession):
        """Test that the pricelist schema in db model validate"""
        model = Pricelists(name="Test Pricelist")
        await save_object(db_session, model)

        db_model = await get_object_by_id(db_session, Pricelists, model.id)
        db_schema_object = PricelistInDB.model_validate(db_model)
        assert db_schema_object == PricelistInDB(
            id=model.id,
            name="Test Pricelist",
            description=None,
            code="TEST-PRICELIST",
            is_active=True,
            sequence=0,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        )

    @pytest.mark.asyncio
    async def test_pricelist_in_db_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the pricelist schema in db model validate"""
        model = Pricelists(name="Test Pricelist")
        await save_object(db_session, model)

        db_model = await get_object_by_id(db_session, Pricelists, model.id)

        db_model.name = "Test Pricelist Updated"

        db_schema_object = PricelistInDB.model_validate(db_model)
        assert db_schema_object == PricelistInDB(
            name="Test Pricelist Updated",
            description=None,
            code="TEST-PRICELIST-UPDATED",
            id=model.id,
            is_active=True,
            sequence=0,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        )


class TestPricelistResponse:
    """Test cases for the pricelist schema response"""

    def test_pricelist_response_inheritance(self):
        """Test that the pricelist schema response inherits from PricelistInDB"""
        assert issubclass(PricelistResponse, PricelistInDB)
        assert issubclass(PricelistResponse, PricelistBase)

    def test_pricelist_response_fields_inheritance(self):
        """Test that the pricelist schema response inherits from PricelistInDB"""
        fields = PricelistResponse.model_fields
        assert len(fields) == 10
        assert 'name' in fields
        assert 'description' in fields
        assert 'code' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        description = fields['description']
        assert description.is_required() is False
        assert description.annotation == Optional[str]
        assert description.default is None

        code = fields['code']
        assert code.is_required() is True
        assert code.annotation == str
        assert code.default is PydanticUndefined

        model_config = PricelistResponse.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_pricelist_response_model_validate(
        self, db_session: AsyncSession
    ):
        """Test that the pricelist schema response model validate"""
        model = Pricelists(name="Test Pricelist")
        await save_object(db_session, model)

        db_model = await get_object_by_id(db_session, Pricelists, model.id)
        db_schema_object = PricelistResponse.model_validate(db_model)
        assert db_schema_object == PricelistResponse(
            id=model.id,
            name="Test Pricelist",
            description=None,
            code="TEST-PRICELIST",
            is_active=True,
            sequence=0,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        )

    @pytest.mark.asyncio
    async def test_pricelist_response_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the pricelist schema response model validate"""
        model = Pricelists(name="Test Pricelist")
        await save_object(db_session, model)

        db_model = await get_object_by_id(db_session, Pricelists, model.id)

        db_model.name = "Test Pricelist Updated"

        db_schema_object = PricelistResponse.model_validate(db_model)
        assert db_schema_object == PricelistResponse(
            name="Test Pricelist Updated",
            description=None,
            code="TEST-PRICELIST-UPDATED",
            id=model.id,
            is_active=True,
            sequence=0,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        )
