from typing import Optional, List, Literal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import StrictStr
from pydantic_core import PydanticUndefined
import pytest

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema,
    StrictPositiveInt
)
from app.schemas.attribute_set_schema import (
    AttributeSetBase, AttributeSetCreate,
    AttributeSetUpdate, AttributeSetInDB,
    AttributeSetResponse, AttributeSummary,
    CategorySummary
)
from app.models.category_type_model import CategoryTypes
from app.models.category_model import Categories
from app.models.attribute_model import Attributes
from app.models.attribute_set_model import AttributeSets
from tests.utils.model_test_utils import save_object


class TestAttributeSetBase:
    """Test cases for the attribute set base schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.attribute_set_dict = {
            "name": "Test Attribute Set"
        }

    def test_attribute_set_base_schema_inheritance(self):
        """Test that the attribute set base schema inherits from BaseSchema"""
        assert issubclass(AttributeSetBase, BaseSchema)

    def test_attribute_set_base_fields_inheritance(self):
        """Test that the attribute set base schema has correct fields"""
        fields = AttributeSetBase.model_fields
        assert len(fields) == 1
        assert 'name' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

    def test_attribute_set_base_schema_input(self):
        schema = AttributeSetBase(**self.attribute_set_dict)
        assert schema.name == "Test Attribute Set"

    def test_attribute_set_base_schema_input_updated(self):
        schema = AttributeSetBase(**self.attribute_set_dict)
        assert schema.name == "Test Attribute Set"

        schema.name = "Test Attribute Set Updated"
        assert schema.name == "Test Attribute Set Updated"

    def test_attribute_set_base_schema_model_dump(self):
        schema = AttributeSetBase(**self.attribute_set_dict)
        assert schema.model_dump() == {
            "name": "Test Attribute Set"
        }

    def test_attribute_set_base_schema_model_dump_json(self):
        schema = AttributeSetBase(**self.attribute_set_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"Test Attribute Set"'\
            '}'


class TestAttributeSetCreate:
    """Test cases for the attribute set create schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.attribute_set_dict = {
            "name": "Test Attribute Set Create",
            "category_id": 1,
            "attribute_ids": [1, 2, 3]
        }

    def test_attribute_set_create_schema_inheritance(self):
        """Test that the attribute set create schema inherits from BaseCreateSchema"""
        assert issubclass(AttributeSetCreate, BaseCreateSchema)
        assert issubclass(AttributeSetCreate, AttributeSetBase)

    def test_attribute_set_create_fields_inheritance(self):
        """Test that the attribute set create schema has correct fields"""
        fields = AttributeSetCreate.model_fields
        assert len(fields) == 5  # 1 base + 2 new + 2 from BaseCreateSchema
        assert 'name' in fields
        assert 'category_id' in fields
        assert 'attribute_ids' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        category_id = fields['category_id']
        assert category_id.is_required() is True
        assert category_id.annotation == int
        assert category_id.default is PydanticUndefined
        assert category_id.metadata[0].strict is True
        assert category_id.metadata[1].gt == 0

        attribute_ids = fields['attribute_ids']
        assert attribute_ids.is_required() is True
        assert attribute_ids.annotation == List[StrictPositiveInt]
        assert attribute_ids.default is PydanticUndefined

    def test_attribute_set_create_schema_input(self):
        schema = AttributeSetCreate(**self.attribute_set_dict)
        assert schema.name == "Test Attribute Set Create"
        assert schema.category_id == 1
        assert schema.attribute_ids == [1, 2, 3]

    def test_attribute_set_create_schema_input_updated(self):
        schema = AttributeSetCreate(**self.attribute_set_dict)
        assert schema.name == "Test Attribute Set Create"
        assert schema.category_id == 1
        assert schema.attribute_ids == [1, 2, 3]

        schema.name = "Test Attribute Set Create Updated"
        assert schema.name == "Test Attribute Set Create Updated"

    def test_attribute_set_create_schema_model_dump(self):
        schema = AttributeSetCreate(**self.attribute_set_dict)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "name": "Test Attribute Set Create",
            "category_id": 1,
            "attribute_ids": [1, 2, 3]
        }

    def test_attribute_set_create_schema_model_dump_json(self):
        schema = AttributeSetCreate(**self.attribute_set_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"name":"Test Attribute Set Create",'\
            '"category_id":1,'\
            '"attribute_ids":[1,2,3]'\
            '}'


class TestAttributeSetUpdate:
    """Test cases for the attribute set update schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.attribute_set_dict = {
            "name": "Test Attribute Set Update",
            "attribute_ids": [4, 5, 6]
        }

    def test_attribute_set_update_schema_inheritance(self):
        """Test that the attribute set update schema inherits from BaseUpdateSchema"""
        assert issubclass(AttributeSetUpdate, BaseUpdateSchema)
        assert issubclass(AttributeSetUpdate, AttributeSetBase)

    def test_attribute_set_update_fields_inheritance(self):
        """Test that the attribute set update schema has correct fields"""
        fields = AttributeSetUpdate.model_fields
        assert len(fields) == 4  # 1 base + 1 new + 2 from BaseUpdateSchema
        assert 'name' in fields
        assert 'attribute_ids' in fields

        name = fields['name']
        assert name.is_required() is False
        assert name.annotation == Optional[StrictStr]
        assert name.default is None
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100

        attribute_ids = fields['attribute_ids']
        assert attribute_ids.is_required() is False
        assert attribute_ids.annotation == List[StrictPositiveInt]
        assert attribute_ids.default_factory == list

    def test_attribute_set_update_schema_input(self):
        schema = AttributeSetUpdate(**self.attribute_set_dict)
        assert schema.name == "Test Attribute Set Update"
        assert schema.attribute_ids == [4, 5, 6]

    def test_attribute_set_update_schema_input_updated(self):
        schema = AttributeSetUpdate(**self.attribute_set_dict)
        assert schema.name == "Test Attribute Set Update"
        assert schema.attribute_ids == [4, 5, 6]

        schema.name = "Test Attribute Set Update Updated"
        assert schema.name == "Test Attribute Set Update Updated"

    def test_attribute_set_update_schema_model_dump(self):
        schema = AttributeSetUpdate(**self.attribute_set_dict)
        assert schema.model_dump() == {
            "is_active": None,
            "sequence": None,
            "name": "Test Attribute Set Update",
            "attribute_ids": [4, 5, 6]
        }

    def test_attribute_set_update_schema_model_dump_json(self):
        schema = AttributeSetUpdate(**self.attribute_set_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":null,'\
            '"sequence":null,'\
            '"name":"Test Attribute Set Update",'\
            '"attribute_ids":[4,5,6]'\
            '}'

    def test_attribute_set_update_schema_default_attribute_ids(self):
        """Test default attribute_ids is empty list"""
        attribute_set_dict = {
            "name": "Test Attribute Set"
        }
        schema = AttributeSetUpdate(**attribute_set_dict)
        assert schema.attribute_ids == []


class TestAttributeSummary:
    """Test cases for the attribute summary schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.attribute_summary_dict = {
            "id": 1,
            "name": "Volume",
            "code": "VOLUME",
            "data_type": "NUMBER",
            "uom": "ml"
        }

    def test_attribute_summary_schema_inheritance(self):
        """Test that the attribute summary schema inherits from BaseSchema"""
        assert issubclass(AttributeSummary, BaseSchema)

    def test_attribute_summary_fields_inheritance(self):
        """Test that the attribute summary schema has correct fields"""
        fields = AttributeSummary.model_fields
        assert len(fields) == 5
        assert 'id' in fields
        assert 'name' in fields
        assert 'code' in fields
        assert 'data_type' in fields
        assert 'uom' in fields

        id_field = fields['id']
        assert id_field.is_required() is True
        assert id_field.annotation == int
        assert id_field.default is PydanticUndefined

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined

        code = fields['code']
        assert code.is_required() is True
        assert code.annotation == str
        assert code.default is PydanticUndefined

        data_type = fields['data_type']
        assert data_type.is_required() is True
        assert data_type.annotation == Literal["TEXT", "NUMBER", "BOOLEAN", "DATE"]
        assert data_type.default is PydanticUndefined

        uom = fields['uom']
        assert uom.is_required() is False
        assert uom.annotation == Optional[str]
        assert uom.default is None

    def test_attribute_summary_schema_input(self):
        schema = AttributeSummary(**self.attribute_summary_dict)
        assert schema.id == 1
        assert schema.name == "Volume"
        assert schema.code == "VOLUME"
        assert schema.data_type == "NUMBER"
        assert schema.uom == "ml"

    def test_attribute_summary_schema_input_updated(self):
        schema = AttributeSummary(**self.attribute_summary_dict)
        assert schema.id == 1
        assert schema.name == "Volume"
        assert schema.code == "VOLUME"
        assert schema.data_type == "NUMBER"
        assert schema.uom == "ml"

        schema.name = "Volume Updated"
        assert schema.name == "Volume Updated"

    def test_attribute_summary_schema_model_dump(self):
        schema = AttributeSummary(**self.attribute_summary_dict)
        assert schema.model_dump() == {
            "id": 1,
            "name": "Volume",
            "code": "VOLUME",
            "data_type": "NUMBER",
            "uom": "ml"
        }

    def test_attribute_summary_schema_model_dump_json(self):
        schema = AttributeSummary(**self.attribute_summary_dict)
        assert schema.model_dump_json() == '{'\
            '"id":1,'\
            '"name":"Volume",'\
            '"code":"VOLUME",'\
            '"data_type":"NUMBER",'\
            '"uom":"ml"'\
            '}'


class TestCategorySummary:
    """Test cases for the category summary schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.category_summary_dict = {
            "id": 1,
            "name": "Test Category",
            "slug": "test-category"
        }

    def test_category_summary_schema_inheritance(self):
        """Test that the category summary schema inherits from BaseSchema"""
        assert issubclass(CategorySummary, BaseSchema)

    def test_category_summary_fields_inheritance(self):
        """Test that the category summary schema has correct fields"""
        fields = CategorySummary.model_fields
        assert len(fields) == 3
        assert 'id' in fields
        assert 'name' in fields
        assert 'slug' in fields

        id_field = fields['id']
        assert id_field.is_required() is True
        assert id_field.annotation == int
        assert id_field.default is PydanticUndefined

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

    def test_category_summary_schema_input(self):
        schema = CategorySummary(**self.category_summary_dict)
        assert schema.id == 1
        assert schema.name == "Test Category"
        assert schema.slug == "test-category"

    def test_category_summary_schema_input_updated(self):
        schema = CategorySummary(**self.category_summary_dict)
        assert schema.id == 1
        assert schema.name == "Test Category"
        assert schema.slug == "test-category"

        schema.name = "Test Category Updated"
        assert schema.name == "Test Category Updated"

    def test_category_summary_schema_model_dump(self):
        schema = CategorySummary(**self.category_summary_dict)
        assert schema.model_dump() == {
            "id": 1,
            "name": "Test Category",
            "slug": "test-category"
        }

    def test_category_summary_schema_model_dump_json(self):
        schema = CategorySummary(**self.category_summary_dict)
        assert schema.model_dump_json() == '{'\
            '"id":1,'\
            '"name":"Test Category",'\
            '"slug":"test-category"'\
            '}'


class TestAttributeSetInDB:
    """Test cases for the attribute set in db schema"""

    def test_attribute_set_in_db_inheritance(self):
        """Test that the attribute set in db schema inherits from BaseInDB"""
        assert issubclass(AttributeSetInDB, BaseInDB)
        assert issubclass(AttributeSetInDB, AttributeSetBase)

    def test_attribute_set_in_db_fields_inheritance(self):
        """Test that the attribute set in db schema has correct fields"""
        fields = AttributeSetInDB.model_fields
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

        model_config = AttributeSetInDB.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_attribute_set_in_db_model_validate(self, db_session: AsyncSession):
        """Test that the attribute set in db schema model validate"""
        # Create category
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        category = Categories(name="Test Category", category_type_id=category_type.id)
        await save_object(db_session, category)

        # Create attributes
        attribute1 = Attributes(name="Volume", data_type="NUMBER", uom="ml")
        attribute2 = Attributes(name="Flavor", data_type="TEXT")
        await save_object(db_session, attribute1)
        await save_object(db_session, attribute2)

        # Create attribute set
        attribute_set = AttributeSets(
            name="Test Attribute Set InDB",
            categories=[category],
            attributes=[attribute1, attribute2]
        )
        await save_object(db_session, attribute_set)

        query = (
            select(AttributeSets)
            .where(AttributeSets.id == attribute_set.id)
            .options(
                selectinload(AttributeSets.categories),
                selectinload(AttributeSets.attributes)
            )
        )
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = AttributeSetInDB.model_validate(db_model)
        assert db_schema_object == AttributeSetInDB(
            id=attribute_set.id,
            name="Test Attribute Set InDB",
            slug="test-attribute-set-indb",
            created_at=attribute_set.created_at,
            updated_at=attribute_set.updated_at,
            created_by=attribute_set.created_by,
            updated_by=attribute_set.updated_by,
            is_active=True,
            sequence=0
        )

    @pytest.mark.asyncio
    async def test_attribute_set_in_db_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the attribute set in db schema model validate updated"""
        # Create category
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        category = Categories(name="Test Category", category_type_id=category_type.id)
        await save_object(db_session, category)

        # Create attributes
        attribute1 = Attributes(name="Volume", data_type="NUMBER", uom="ml")
        attribute2 = Attributes(name="Flavor", data_type="TEXT")
        await save_object(db_session, attribute1)
        await save_object(db_session, attribute2)

        # Create attribute set
        attribute_set = AttributeSets(
            name="Test Attribute Set InDB",
            categories=[category],
            attributes=[attribute1, attribute2]
        )
        await save_object(db_session, attribute_set)

        query = (
            select(AttributeSets)
            .where(AttributeSets.id == attribute_set.id)
            .options(
                selectinload(AttributeSets.categories),
                selectinload(AttributeSets.attributes)
            )
        )
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Test Attribute Set InDB Updated"
        db_model.categories[0].name = "Test Category Updated"
        db_model.attributes[0].name = "Volume Updated"

        db_schema_object = AttributeSetInDB.model_validate(db_model)
        assert db_schema_object == AttributeSetInDB(
            id=attribute_set.id,
            name="Test Attribute Set InDB Updated",
            slug="test-attribute-set-indb-updated",
            created_at=attribute_set.created_at,
            updated_at=attribute_set.updated_at,
            created_by=attribute_set.created_by,
            updated_by=attribute_set.updated_by,
            is_active=True,
            sequence=0
        )


class TestAttributeSetResponse:
    """Test cases for the attribute set response schema"""

    def test_attribute_set_response_inheritance(self):
        """Test that the attribute set response schema inherits from AttributeSetInDB"""
        assert issubclass(AttributeSetResponse, AttributeSetInDB)

    def test_attribute_set_response_fields_inheritance(self):
        """Test that the attribute set response schema has correct fields"""
        fields = AttributeSetResponse.model_fields
        assert len(fields) == 11  # Same as AttributeSetInDB
        assert 'name' in fields
        assert 'slug' in fields
        assert 'categories' in fields
        assert 'attributes' in fields

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

        categories = fields['categories']
        assert categories.is_required() is True
        assert categories.annotation == List[CategorySummary]
        assert categories.default is PydanticUndefined

        attributes = fields['attributes']
        assert attributes.is_required() is True
        assert attributes.annotation == List[AttributeSummary]
        assert attributes.default is PydanticUndefined

        model_config = AttributeSetResponse.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_attribute_set_response_model_validate(
        self, db_session: AsyncSession
    ):
        """Test that the attribute set response schema model validate"""
        # Create category
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        category = Categories(
            name="Test Category Response",
            category_type_id=category_type.id
        )
        await save_object(db_session, category)

        # Create attributes
        attribute1 = Attributes(name="Weight", data_type="NUMBER", uom="kg")
        attribute2 = Attributes(name="Color", data_type="TEXT")
        await save_object(db_session, attribute1)
        await save_object(db_session, attribute2)

        # Create attribute set
        attribute_set = AttributeSets(
            name="Test Attribute Set Response",
            categories=[category],
            attributes=[attribute1, attribute2]
        )
        await save_object(db_session, attribute_set)

        query = (
            select(AttributeSets)
            .where(AttributeSets.id == attribute_set.id)
            .options(
                selectinload(AttributeSets.categories),
                selectinload(AttributeSets.attributes)
            )
        )
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = AttributeSetResponse.model_validate(db_model)

        assert db_schema_object == AttributeSetResponse(
            id=attribute_set.id,
            name="Test Attribute Set Response",
            slug="test-attribute-set-response",
            categories=[CategorySummary(
                id=category.id,
                name="Test Category Response",
                slug="test-category-response"
            )],
            attributes=[
                AttributeSummary(
                    id=attribute1.id,
                    name="Weight",
                    code="WEIGHT",
                    data_type="NUMBER",
                    uom="kg"
                ),
                AttributeSummary(
                    id=attribute2.id,
                    name="Color",
                    code="COLOR",
                    data_type="TEXT",
                    uom=None
                )
            ],
            created_at=attribute_set.created_at,
            updated_at=attribute_set.updated_at,
            created_by=attribute_set.created_by,
            updated_by=attribute_set.updated_by,
            is_active=True,
            sequence=0
        )

    @pytest.mark.asyncio
    async def test_attribute_set_response_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the attribute set response schema model validate updated"""
        # Create category
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        category = Categories(
            name="Test Category Response",
            category_type_id=category_type.id
        )
        await save_object(db_session, category)

        # Create attributes
        attribute1 = Attributes(name="Weight", data_type="NUMBER", uom="kg")
        attribute2 = Attributes(name="Color", data_type="TEXT")
        await save_object(db_session, attribute1)
        await save_object(db_session, attribute2)

        # Create attribute set
        attribute_set = AttributeSets(
            name="Test Attribute Set Response",
            categories=[category],
            attributes=[attribute1, attribute2]
        )
        await save_object(db_session, attribute_set)

        query = (
            select(AttributeSets)
            .where(AttributeSets.id == attribute_set.id)
            .options(
                selectinload(AttributeSets.categories),
                selectinload(AttributeSets.attributes)
            )
        )
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Test Attribute Set Response Updated"
        db_model.categories[0].name = "Test Category Response Updated"
        db_model.attributes[0].name = "Weight Updated"
        db_model.attributes[1].uom = "pieces"

        db_schema_object = AttributeSetResponse.model_validate(db_model)
        assert db_schema_object == AttributeSetResponse(
            id=attribute_set.id,
            name="Test Attribute Set Response Updated",
            slug="test-attribute-set-response-updated",
            categories=[CategorySummary(
                id=category.id,
                name="Test Category Response Updated",
                slug="test-category-response-updated"
            )],
            attributes=[
                AttributeSummary(
                    id=attribute1.id,
                    name="Weight Updated",
                    code="WEIGHT-UPDATED",
                    data_type="NUMBER",
                    uom="kg"
                ),
                AttributeSummary(
                    id=attribute2.id,
                    name="Color",
                    code="COLOR",
                    data_type="TEXT",
                    uom="pieces"
                )
            ],
            created_at=attribute_set.created_at,
            updated_at=attribute_set.updated_at,
            created_by=attribute_set.created_by,
            updated_by=attribute_set.updated_by,
            is_active=True,
            sequence=0
        )
