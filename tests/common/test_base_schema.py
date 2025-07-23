from typing import Optional
from datetime import datetime

from sqlalchemy import Column, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, StrictBool
from pydantic_core import PydanticUndefined
import pytest

from app.core.base import Base
from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema, StrictNonNegativeInt
)
from tests.utils.model_test_utils import save_object


class SampleModelBase(Base):
    """Sample model for Base functionality testing."""
    name = Column(String, nullable=False)
    description = Column(Text)


class SampleSchemaBase(BaseSchema):
    """Sample schema for base testing"""
    name: str


class SampleSchemaCreate(SampleSchemaBase, BaseCreateSchema):
    """Sample schema for creating a new sample"""
    pass


class SampleSchemaUpdate(SampleSchemaBase, BaseUpdateSchema):
    """Schema for updating an existing sample"""
    name: Optional[str] = None
    description: Optional[str] = None


class SampleSchemaInDB(SampleSchemaBase, BaseInDB):
    """Schema for Sample as stored in database"""
    description: str


class SampleSchemaResponse(SampleSchemaInDB):
    """Schema for Sample API responses"""
    pass


class TestSampleSchemaBase:
    """Test cases for the base schema"""

    def test_base_schema_inheritance(self):
        """Test that the base schema inherits from BaseSchema"""
        assert issubclass(SampleSchemaBase, BaseSchema)
        assert issubclass(SampleSchemaBase, BaseModel)
        assert issubclass(BaseSchema, BaseModel)


class TestSampleSchemaCreate:
    """Test cases for the sample schema create"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.sample_dict = {
            "name": "Test Sample",
            "is_active": False,
            "sequence": 1
        }

    def test_base_schema_create_inheritance(self):
        """Test that the base schema create inherits from BaseCreateSchema"""
        assert issubclass(SampleSchemaCreate, BaseCreateSchema)
        assert issubclass(SampleSchemaCreate, SampleSchemaBase)
        assert issubclass(BaseCreateSchema, BaseSchema)
        assert issubclass(BaseCreateSchema, BaseModel)

    def test_base_fields_inheritance(self):
        """Test that the base schema create inherits from BaseCreateSchema"""
        fields = SampleSchemaCreate.model_fields
        assert len(fields) == 3
        assert 'name' in fields
        assert 'is_active' in fields
        assert 'sequence' in fields

        is_active = fields['is_active']
        assert is_active.is_required() is False
        assert is_active.annotation == bool
        assert is_active.default is True
        assert is_active.metadata[0].strict is True

        sequence = fields['sequence']
        assert sequence.is_required() is False
        assert sequence.annotation == int
        assert sequence.default == 0
        assert sequence.metadata[0].strict is True
        assert sequence.metadata[1].ge == 0

    def test_base_schema_create_input(self):
        schema = SampleSchemaCreate(**self.sample_dict)
        assert schema.is_active is False
        assert schema.sequence == 1

    def test_base_schema_create_input_updated(self):
        schema = SampleSchemaCreate(**self.sample_dict)
        assert schema.sequence == 1
        assert schema.is_active is False

        schema.sequence = 2
        assert schema.sequence == 2
        assert schema.is_active is False

    def test_base_schema_create_model_dump(self):
        schema = SampleSchemaCreate(**self.sample_dict)
        assert schema.model_dump() == {
            "name": "Test Sample",
            "is_active": False,
            "sequence": 1
        }

    def test_base_schema_create_model_dump_json(self):
        schema = SampleSchemaCreate(**self.sample_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":false,'\
            '"sequence":1,'\
            '"name":"Test Sample"'\
            '}'


class TestSampleSchemaUpdate:
    """Test cases for the sample schema update"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.sample_dict = {
            "name": "Test Sample",
            "is_active": False,
            "sequence": 1
        }

    def test_base_schema_update_inheritance(self):
        """Test that the base schema update inherits from BaseUpdateSchema"""
        assert issubclass(SampleSchemaUpdate, BaseUpdateSchema)
        assert issubclass(SampleSchemaUpdate, SampleSchemaBase)
        assert issubclass(BaseUpdateSchema, BaseSchema)
        assert issubclass(BaseUpdateSchema, BaseModel)

    def test_base_fields_inheritance(self):
        """Test that the base schema update inherits from BaseUpdateSchema"""
        fields = SampleSchemaUpdate.model_fields
        assert len(fields) == 4
        assert 'name' in fields
        assert 'is_active' in fields
        assert 'sequence' in fields
        assert 'description' in fields

        is_active = fields['is_active']
        assert is_active.is_required() is False
        assert is_active.annotation == Optional[StrictBool]
        assert is_active.default is None

        sequence = fields['sequence']
        assert sequence.is_required() is False
        assert sequence.annotation == Optional[StrictNonNegativeInt]
        assert sequence.default is None

    def test_base_schema_update_input(self):
        schema = SampleSchemaUpdate(**self.sample_dict)
        assert schema.is_active is False
        assert schema.sequence == 1

    def test_base_schema_update_input_updated(self):
        schema = SampleSchemaUpdate(**self.sample_dict)
        assert schema.is_active is False
        assert schema.sequence == 1

        schema.sequence = 2
        assert schema.sequence == 2
        assert schema.is_active is False

    def test_base_schema_update_model_dump(self):
        schema = SampleSchemaUpdate(**self.sample_dict)
        assert schema.model_dump() == {
            "name": "Test Sample",
            "description": None,
            "is_active": False,
            "sequence": 1
        }

    def test_base_schema_update_model_dump_json(self):
        schema = SampleSchemaUpdate(**self.sample_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":false,'\
            '"sequence":1,'\
            '"name":"Test Sample",'\
            '"description":null'\
            '}'


class TestSampleSchemaInDB:
    """Test cases for the sample schema in db"""

    def test_base_schema_in_db_inheritance(self):
        """Test that the base schema in db inherits from BaseInDB"""
        assert issubclass(SampleSchemaInDB, BaseInDB)
        assert issubclass(SampleSchemaInDB, SampleSchemaBase)
        assert issubclass(BaseInDB, BaseSchema)
        assert issubclass(BaseInDB, BaseModel)

    def test_base_fields_inheritance(self):
        """Test that the base schema in db inherits from BaseInDB"""
        fields = SampleSchemaInDB.model_fields
        assert len(fields) == 9
        assert 'name' in fields
        assert 'description' in fields
        assert 'id' in fields
        assert 'is_active' in fields
        assert 'sequence' in fields
        assert 'created_at' in fields
        assert 'updated_at' in fields
        assert 'created_by' in fields
        assert 'updated_by' in fields

        id = fields['id']
        assert id.is_required() is True
        assert id.annotation == int
        assert id.default is PydanticUndefined

        created_at = fields['created_at']
        assert created_at.is_required() is True
        assert created_at.annotation == datetime
        assert created_at.default is PydanticUndefined

        updated_at = fields['updated_at']
        assert updated_at.is_required() is True
        assert updated_at.annotation == datetime
        assert updated_at.default is PydanticUndefined

        created_by = fields['created_by']
        assert created_by.is_required() is True
        assert created_by.annotation == int
        assert created_by.default is PydanticUndefined

        updated_by = fields['updated_by']
        assert updated_by.is_required() is True
        assert updated_by.annotation == int
        assert updated_by.default is PydanticUndefined

        is_active = fields['is_active']
        assert is_active.is_required() is True
        assert is_active.annotation == bool
        assert is_active.default is PydanticUndefined

        sequence = fields['sequence']
        assert sequence.is_required() is True
        assert sequence.annotation == int
        assert sequence.default is PydanticUndefined

        model_config = SampleSchemaInDB.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_base_schema_in_db_model_validate(self, db_session: AsyncSession):
        """Test that the base schema in db model validate"""
        schema = SampleModelBase(name="Test Sample", description="Test Description")
        await save_object(db_session, schema)

        stmt = select(SampleModelBase).where(SampleModelBase.id == schema.id)
        result = await db_session.execute(stmt)
        db_schema = result.scalar_one_or_none()
        db_schema_object = SampleSchemaInDB.model_validate(db_schema)
        assert db_schema_object == SampleSchemaInDB(
            name="Test Sample",
            description="Test Description",
            id=schema.id,
            is_active=True,
            sequence=0,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            created_by=schema.created_by,
            updated_by=schema.updated_by
        )

    @pytest.mark.asyncio
    async def test_base_schema_in_db_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the base schema in db model validate"""
        schema = SampleModelBase(name="Test Sample", description="Test Description")
        await save_object(db_session, schema)

        stmt = select(SampleModelBase).where(SampleModelBase.id == schema.id)
        result = await db_session.execute(stmt)
        db_schema = result.scalar_one_or_none()

        db_schema.name = "Test Sample Updated"

        db_schema_object = SampleSchemaInDB.model_validate(db_schema)
        assert db_schema_object == SampleSchemaInDB(
            name="Test Sample Updated",
            description="Test Description",
            id=schema.id,
            is_active=True,
            sequence=0,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            created_by=schema.created_by,
            updated_by=schema.updated_by
        )


class TestSampleSchemaResponse:
    """Test cases for the sample schema response"""

    def test_base_schema_response_inheritance(self):
        """Test that the base schema response inherits from BaseSchema"""
        assert issubclass(SampleSchemaResponse, SampleSchemaInDB)
        assert issubclass(SampleSchemaResponse, SampleSchemaBase)

    def test_base_fields_inheritance(self):
        """Test that the base schema response inherits from SampleSchemaInDB"""
        fields = SampleSchemaResponse.model_fields
        assert len(fields) == 9
        assert 'name' in fields
        assert 'description' in fields
        assert 'id' in fields
        assert 'is_active' in fields
        assert 'sequence' in fields
        assert 'created_at' in fields
        assert 'updated_at' in fields
        assert 'created_by' in fields
        assert 'updated_by' in fields

        id = fields['id']
        assert id.is_required() is True
        assert id.annotation == int
        assert id.default is PydanticUndefined

        created_at = fields['created_at']
        assert created_at.is_required() is True
        assert created_at.annotation == datetime
        assert created_at.default is PydanticUndefined

        updated_at = fields['updated_at']
        assert updated_at.is_required() is True
        assert updated_at.annotation == datetime
        assert updated_at.default is PydanticUndefined

        created_by = fields['created_by']
        assert created_by.is_required() is True
        assert created_by.annotation == int
        assert created_by.default is PydanticUndefined

        updated_by = fields['updated_by']
        assert updated_by.is_required() is True
        assert updated_by.annotation == int
        assert updated_by.default is PydanticUndefined

        is_active = fields['is_active']
        assert is_active.is_required() is True
        assert is_active.annotation == bool
        assert is_active.default is PydanticUndefined

        sequence = fields['sequence']
        assert sequence.is_required() is True
        assert sequence.annotation == int
        assert sequence.default is PydanticUndefined

        model_config = SampleSchemaResponse.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_base_schema_response_model_validate(self, db_session: AsyncSession):
        """Test that the base schema response model validate"""
        schema = SampleModelBase(name="Test Sample", description="Test Description")
        await save_object(db_session, schema)

        stmt = select(SampleModelBase).where(SampleModelBase.id == schema.id)
        result = await db_session.execute(stmt)
        db_schema = result.scalar_one_or_none()
        db_schema_object = SampleSchemaResponse.model_validate(db_schema)
        assert db_schema_object == SampleSchemaResponse(
            name="Test Sample",
            description="Test Description",
            id=schema.id,
            is_active=True,
            sequence=0,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            created_by=schema.created_by,
            updated_by=schema.updated_by
        )

    @pytest.mark.asyncio
    async def test_base_schema_response_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the base schema response model validate"""
        schema = SampleModelBase(name="Test Sample", description="Test Description")
        await save_object(db_session, schema)

        stmt = select(SampleModelBase).where(SampleModelBase.id == schema.id)
        result = await db_session.execute(stmt)
        db_schema = result.scalar_one_or_none()

        db_schema.name = "Test Sample Updated"

        db_schema_object = SampleSchemaResponse.model_validate(db_schema)
        assert db_schema_object == SampleSchemaResponse(
            name="Test Sample Updated",
            description="Test Description",
            id=schema.id,
            is_active=True,
            sequence=0,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            created_by=schema.created_by,
            updated_by=schema.updated_by
        )
