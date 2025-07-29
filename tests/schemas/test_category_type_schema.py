from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import StrictStr
from pydantic_core import PydanticUndefined
import pytest

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema
)
from app.schemas.category_type_schema import (
    CategoryTypeBase, CategoryTypeCreate,
    CategoryTypeUpdate, CategoryTypeInDB,
    CategoryTypeResponse
)
from app.models import CategoryTypes
from tests.utils.model_test_utils import save_object, get_object_by_id


class TestCategoryTypeBase:
    """Test cases for the category type base schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.category_type_dict = {"name": "Test Category Type"}

    def test_category_type_base_schema_inheritance(self):
        """Test that the category type base schema inherits from BaseSchema"""
        assert issubclass(CategoryTypeBase, BaseSchema)

    def test_category_type_base_fields_inheritance(self):
        """Test that the category type base schema inherits from BaseSchema"""
        fields = CategoryTypeBase.model_fields
        assert len(fields) == 1
        assert 'name' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

    def test_category_type_base_schema_input(self):
        schema = CategoryTypeBase(**self.category_type_dict)
        assert schema.name == "Test Category Type"

    def test_category_type_base_schema_input_updated(self):
        schema = CategoryTypeBase(**self.category_type_dict)
        assert schema.name == "Test Category Type"

        schema.name = "Test Category Type Updated"
        assert schema.name == "Test Category Type Updated"

    def test_category_type_base_schema_model_dump(self):
        schema = CategoryTypeBase(**self.category_type_dict)
        assert schema.model_dump() == {
            "name": "Test Category Type"
        }

    def test_category_type_base_schema_model_dump_json(self):
        schema = CategoryTypeBase(**self.category_type_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"Test Category Type"'\
            '}'


class TestCategoryTypeCreate:
    """Test cases for the category type schema create"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.category_type_dict = {"name": "Test Category Type"}

    def test_category_type_create_schema_inheritance(self):
        """Test that the category type create schema inherits from BaseCreateSchema"""
        assert issubclass(CategoryTypeCreate, BaseCreateSchema)
        assert issubclass(CategoryTypeCreate, CategoryTypeBase)

    def test_category_type_create_fields_inheritance(self):
        """Test that the category type create schema inherits from BaseCreateSchema"""
        fields = CategoryTypeCreate.model_fields
        assert len(fields) == 3
        assert 'name' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

    def test_category_type_create_schema_input(self):
        schema = CategoryTypeCreate(**self.category_type_dict)
        assert schema.name == "Test Category Type"

    def test_category_type_create_schema_input_updated(self):
        schema = CategoryTypeCreate(**self.category_type_dict)
        assert schema.name == "Test Category Type"

        schema.name = "Test Category Type Updated"
        assert schema.name == "Test Category Type Updated"

    def test_category_type_create_schema_model_dump(self):
        schema = CategoryTypeCreate(**self.category_type_dict)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "name": "Test Category Type"
        }

    def test_category_type_create_schema_model_dump_json(self):
        schema = CategoryTypeCreate(**self.category_type_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"name":"Test Category Type"'\
            '}'


class TestCategoryTypeUpdate:
    """Test cases for the category type schema update"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.category_type_dict = {"name": "Test Category Type"}

    def test_category_type_update_schema_inheritance(self):
        """Test that the category type update schema inherits from BaseUpdateSchema"""
        assert issubclass(CategoryTypeUpdate, BaseUpdateSchema)
        assert issubclass(CategoryTypeUpdate, CategoryTypeBase)

    def test_category_type_update_fields_inheritance(self):
        """Test that the category type update schema inherits from BaseUpdateSchema"""
        fields = CategoryTypeUpdate.model_fields
        assert len(fields) == 3
        assert 'name' in fields

        name = fields['name']
        assert name.is_required() is False
        assert name.annotation == Optional[StrictStr]
        assert name.default is None
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100

    def test_category_type_update_schema_input(self):
        schema = CategoryTypeUpdate(**self.category_type_dict)
        assert schema.name == "Test Category Type"

    def test_category_type_update_schema_input_updated(self):
        schema = CategoryTypeUpdate(**self.category_type_dict)
        assert schema.name == "Test Category Type"

        schema.name = "Test Category Type Updated"
        assert schema.name == "Test Category Type Updated"

    def test_category_type_update_schema_model_dump(self):
        schema = CategoryTypeUpdate(**self.category_type_dict)
        assert schema.model_dump() == {
            "is_active": None,
            "sequence": None,
            "name": "Test Category Type"
        }

    def test_category_type_update_schema_model_dump_json(self):
        schema = CategoryTypeUpdate(**self.category_type_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":null,'\
            '"sequence":null,'\
            '"name":"Test Category Type"'\
            '}'


class TestCategoryTypeInDB:
    """Test cases for the category type schema in db"""

    def test_category_type_in_db_inheritance(self):
        """Test that the category type schema in db inherits from BaseInDB"""
        assert issubclass(CategoryTypeInDB, BaseInDB)
        assert issubclass(CategoryTypeInDB, CategoryTypeBase)

    def test_category_type_in_db_fields_inheritance(self):
        """Test that the category type schema in db inherits from BaseInDB"""
        fields = CategoryTypeInDB.model_fields
        assert len(fields) == 9
        assert 'name' in fields
        assert 'slug' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        model_config = CategoryTypeInDB.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_category_type_in_db_model_validate(self, db_session: AsyncSession):
        """Test that the category type schema in db model validate"""
        model = CategoryTypes(name="Test Category Type")
        await save_object(db_session, model)

        db_model = await get_object_by_id(db_session, CategoryTypes, model.id)
        db_schema_object = CategoryTypeInDB.model_validate(db_model)
        assert db_schema_object == CategoryTypeInDB(
            id=model.id,
            name="Test Category Type",
            slug="test-category-type",
            is_active=True,
            sequence=0,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        )

    @pytest.mark.asyncio
    async def test_category_type_in_db_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the category type schema in db model validate"""
        model = CategoryTypes(name="Test Category Type")
        await save_object(db_session, model)

        db_model = await get_object_by_id(db_session, CategoryTypes, model.id)

        db_model.name = "Test Category Type Updated"

        db_schema_object = CategoryTypeInDB.model_validate(db_model)
        assert db_schema_object == CategoryTypeInDB(
            name="Test Category Type Updated",
            slug="test-category-type-updated",
            id=model.id,
            is_active=True,
            sequence=0,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        )


class TestCategoryTypeResponse:
    """Test cases for the category type schema response"""

    def test_category_type_response_inheritance(self):
        """Test that the category type schema response inherits from CategoryTypeInDB"""
        assert issubclass(CategoryTypeResponse, CategoryTypeInDB)
        assert issubclass(CategoryTypeResponse, CategoryTypeBase)

    def test_category_type_response_fields_inheritance(self):
        """Test that the category type schema response inherits from CategoryTypeInDB"""
        fields = CategoryTypeResponse.model_fields
        assert len(fields) == 9
        assert 'name' in fields
        assert 'slug' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        model_config = CategoryTypeResponse.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_category_type_response_model_validate(
        self, db_session: AsyncSession
    ):
        """Test that the category type schema response model validate"""
        model = CategoryTypes(name="Test Category Type")
        await save_object(db_session, model)

        db_model = await get_object_by_id(db_session, CategoryTypes, model.id)
        db_schema_object = CategoryTypeResponse.model_validate(db_model)
        assert db_schema_object == CategoryTypeResponse(
            id=model.id,
            name="Test Category Type",
            slug="test-category-type",
            is_active=True,
            sequence=0,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        )

    @pytest.mark.asyncio
    async def test_category_type_response_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the category type schema response model validate"""
        model = CategoryTypes(name="Test Category Type")
        await save_object(db_session, model)

        db_model = await get_object_by_id(db_session, CategoryTypes, model.id)

        db_model.name = "Test Category Type Updated"

        db_schema_object = CategoryTypeResponse.model_validate(db_model)
        assert db_schema_object == CategoryTypeResponse(
            name="Test Category Type Updated",
            slug="test-category-type-updated",
            id=model.id,
            is_active=True,
            sequence=0,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        )
