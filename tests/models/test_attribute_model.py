from sqlalchemy import String, event, Enum as SAEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
import pytest

from app.core.base import Base
from app.models.attribute_model import Attributes, DataType
from app.models.attribute_set_model import AttributeSets
from app.core.listeners import _set_code
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    count_model_objects,
    assert_relationship
)


class TestAttribute:
    """Test suite for Attribute model"""

    @pytest.fixture(autouse=True)
    async def setup_objects(self, db_session: AsyncSession):
        """Setup method for the test suite"""
        self.test_attribute1 = Attributes(
            name="test attribute 1",
            uom="test uom 1"
        )
        await save_object(db_session, self.test_attribute1)

        self.test_attribute2 = Attributes(
            name="test attribute 2"
        )
        await save_object(db_session, self.test_attribute2)

    def test_inheritance_from_base_model(self):
        """Test that Attribute model inherits from Base model"""
        assert issubclass(Attributes, Base)

    def test_fields_with_validation(self):
        """Test that the fields have the expected validation"""
        assert not hasattr(Attributes, 'validate_name')
        assert len(Attributes.__mapper__.validators) == 0

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(Attributes.name, 'set', _set_code)
        assert not event.contains(Attributes, 'set', _set_code)

    def test_has_methods(self):
        """Test that the model has the expected static methods"""
        assert hasattr(Attributes, 'validate_value_for_data_type')
        assert hasattr(Attributes, 'convert_value_to_python')

        assert isinstance(
            Attributes.__dict__['validate_value_for_data_type'],
            staticmethod
        )
        assert isinstance(Attributes.__dict__['convert_value_to_python'], staticmethod)

    def test_name_field_properties(self):
        """Test the properties of the name field"""
        name_column = Attributes.__table__.columns.get('name')
        assert name_column is not None
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 50
        assert name_column.nullable is False
        assert name_column.unique is None
        assert name_column.index is True
        assert name_column.default is None

    def test_code_field_properties(self):
        """Test the properties of the code field"""
        code_column = Attributes.__table__.columns.get('code')
        assert code_column is not None
        assert isinstance(code_column.type, String)
        assert code_column.type.length == 50
        assert code_column.nullable is False
        assert code_column.unique is True
        assert code_column.index is True
        assert code_column.default is None

    def test_data_type_field_properties(self):
        """Test the properties of the data_type field"""
        data_type_column = Attributes.__table__.columns.get('data_type')
        assert data_type_column is not None
        assert isinstance(data_type_column.type, SAEnum)
        assert data_type_column.type.enum_class == DataType
        assert data_type_column.nullable is False
        assert data_type_column.unique is None
        assert data_type_column.index is True
        assert data_type_column.default.arg == DataType.TEXT

    def test_uom_field_properties(self):
        """Test the properties of the uom field"""
        uom_column = Attributes.__table__.columns.get('uom')
        assert uom_column is not None
        assert isinstance(uom_column.type, String)
        assert uom_column.type.length == 15
        assert uom_column.nullable is True
        assert uom_column.unique is None
        assert uom_column.index is None
        assert uom_column.default is None

    def test_relationships_with_other_models(self):
        """Test the relationships with other models"""
        assert_relationship(
            Attributes, "attribute_sets", "attributes"
        )
        assert_relationship(
            Attributes, "sku_attribute_values", "attribute"
        )

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_attribute1)
        assert str_repr == "Attributes(test attribute 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        await db_session.refresh(self.test_attribute1, ['sku_attribute_values'])
        await db_session.refresh(self.test_attribute1, ['attribute_sets'])

        await db_session.refresh(self.test_attribute2, ['sku_attribute_values'])
        await db_session.refresh(self.test_attribute2, ['attribute_sets'])

        assert self.test_attribute1.id == 1
        assert self.test_attribute1.name == "test attribute 1"
        assert self.test_attribute1.code == "TEST-ATTRIBUTE-1"
        assert self.test_attribute1.data_type == DataType.TEXT
        assert self.test_attribute1.uom == "test uom 1"
        assert self.test_attribute1.sku_attribute_values == []
        assert self.test_attribute1.attribute_sets == []

        assert self.test_attribute2.id == 2
        assert self.test_attribute2.name == "test attribute 2"
        assert self.test_attribute2.code == "TEST-ATTRIBUTE-2"
        assert self.test_attribute2.data_type == DataType.TEXT
        assert self.test_attribute2.uom is None
        assert self.test_attribute2.sku_attribute_values == []
        assert self.test_attribute2.attribute_sets == []

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = Attributes(
            name="test attribute 3",
            data_type=DataType.BOOLEAN,
            uom="test uom 3"
        )
        await save_object(db_session, item)

        assert item.id == 3
        assert item.name == "test attribute 3"
        assert item.code == "TEST-ATTRIBUTE-3"
        assert item.data_type == DataType.BOOLEAN
        assert item.uom == "test uom 3"
        assert await count_model_objects(db_session, Attributes) == 3

        # Test default data_type
        item_with_default = Attributes(
            name="test attribute 4"
        )
        await save_object(db_session, item_with_default)
        assert item_with_default.id == 4
        assert item_with_default.name == "test attribute 4"
        assert item_with_default.code == "TEST-ATTRIBUTE-4"
        assert item_with_default.data_type == DataType.TEXT
        assert item_with_default.uom is None
        assert await count_model_objects(db_session, Attributes) == 4

        item_with_code = Attributes(
            name="test attribute 5",
            code="code_attribute_5",
            uom="test uom 5"
        )
        await save_object(db_session, item_with_code)
        assert item_with_code.id == 5
        assert item_with_code.name == "test attribute 5"
        # code should be set to the slugified name
        assert item_with_code.code == "TEST-ATTRIBUTE-5"
        assert item_with_code.uom == "test uom 5"
        assert await count_model_objects(db_session, Attributes) == 5

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(db_session, Attributes, self.test_attribute1.id)
        assert item.id == 1
        assert item.name == "test attribute 1"
        assert item.code == "TEST-ATTRIBUTE-1"
        assert item.data_type == DataType.TEXT
        assert item.uom == "test uom 1"

        item = await get_object_by_id(db_session, Attributes, self.test_attribute2.id)
        assert item.id == 2
        assert item.name == "test attribute 2"
        assert item.code == "TEST-ATTRIBUTE-2"
        assert item.data_type == DataType.TEXT
        assert item.uom is None

        items = await get_all_objects(db_session, Attributes)
        assert len(items) == 2
        assert items[0].name == "test attribute 1"
        assert items[0].code == "TEST-ATTRIBUTE-1"
        assert items[0].data_type == DataType.TEXT
        assert items[0].uom == "test uom 1"
        assert items[1].name == "test attribute 2"
        assert items[1].code == "TEST-ATTRIBUTE-2"
        assert items[1].data_type == DataType.TEXT
        assert items[1].uom is None

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(db_session, Attributes, 1)
        item.name = "Primary Color"
        item.uom = "RGB"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "Primary Color"
        assert item.code == "PRIMARY-COLOR"  # Should change on name update
        assert item.uom == "RGB"
        assert await count_model_objects(db_session, Attributes) == 2

        item.code = "updated-code-attribute-1"
        await save_object(db_session, item)
        assert item.id == 1
        assert item.name == "Primary Color"
        # code should not change
        assert item.code == "PRIMARY-COLOR"
        assert item.uom == "RGB"
        assert await count_model_objects(db_session, Attributes) == 2

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_attribute2)

        item = await get_object_by_id(
            db_session, Attributes, self.test_attribute2.id
        )
        assert item is None
        assert await count_model_objects(db_session, Attributes) == 1

    """
    ================================================
    Relationship Tests (Attributes -> AttributeSets)
    ================================================
    """

    @pytest.mark.asyncio
    async def test_create_attribute_with_sets(
        self, db_session: AsyncSession
    ):
        """Test creating an attribute and associating it with multiple sets"""
        attribute = Attributes(
            name="Test Attribute with Attribute Sets",
            attribute_sets=[
                AttributeSets(name="Test Attribute Set 1"),
                AttributeSets(name="Test Attribute Set 2")
            ]
        )
        await save_object(db_session, attribute)

        retrieved_attribute = await get_object_by_id(
            db_session,
            Attributes,
            attribute.id
        )

        await db_session.refresh(retrieved_attribute, ['attribute_sets'])

        assert retrieved_attribute.id == 3
        assert retrieved_attribute.name == "Test Attribute with Attribute Sets"
        assert len(retrieved_attribute.attribute_sets) == 2
        assert retrieved_attribute.attribute_sets[0].name == "Test Attribute Set 1"
        assert retrieved_attribute.attribute_sets[1].name == "Test Attribute Set 2"

    @pytest.mark.asyncio
    async def test_add_multiple_attribute_sets_to_attribute(
        self, db_session: AsyncSession
    ):
        """Test adding multiple attributes to an attribute set"""
        attribute_sets = []
        for i in range(5):
            attribute_set = AttributeSets(
                name=f"Test Attribute Set {i}",
                attributes=[self.test_attribute1]
            )
            await save_object(db_session, attribute_set)
            attribute_sets.append(attribute_set)

        retrieved_attribute = await get_object_by_id(
            db_session,
            Attributes,
            self.test_attribute1.id
        )

        await db_session.refresh(retrieved_attribute, ['attribute_sets'])

        assert len(retrieved_attribute.attribute_sets) == 5
        for i in range(5):
            assert retrieved_attribute.attribute_sets[i].id == i + 1
            assert retrieved_attribute.attribute_sets[i].name == (
                f"Test Attribute Set {i}"
            )
            assert retrieved_attribute.attribute_sets[i].slug == (
                f"test-attribute-set-{i}"
            )

    @pytest.mark.asyncio
    async def test_update_attribute_attribute_sets(
        self, db_session: AsyncSession
    ):
        """Test updating the attribute's attribute sets"""
        attribute = await get_object_by_id(
            db_session,
            Attributes,
            self.test_attribute1.id
        )
        await db_session.refresh(attribute, ['attribute_sets'])
        assert len(attribute.attribute_sets) == 0

        attribute.attribute_sets = [
            AttributeSets(name="Test Attribute Set 1"),
            AttributeSets(name="Test Attribute Set 2")
        ]
        await save_object(db_session, attribute)
        await db_session.refresh(attribute, ['attribute_sets'])
        assert len(attribute.attribute_sets) == 2
        assert attribute.attribute_sets[0].name == "Test Attribute Set 1"
        assert attribute.attribute_sets[1].name == "Test Attribute Set 2"

        attribute.attribute_sets = [
            AttributeSets(name="Test Attribute Set 3"),
            AttributeSets(name="Test Attribute Set 4"),
            AttributeSets(name="Test Attribute Set 5")
        ]
        await save_object(db_session, attribute)
        await db_session.refresh(attribute, ['attribute_sets'])
        assert len(attribute.attribute_sets) == 3
        assert attribute.attribute_sets[0].name == "Test Attribute Set 3"
        assert attribute.attribute_sets[1].name == "Test Attribute Set 4"
        assert attribute.attribute_sets[2].name == "Test Attribute Set 5"

    @pytest.mark.asyncio
    async def test_remove_attribute_from_set(
        self, db_session: AsyncSession
    ):
        """Test removing an attribute from a set without deleting the attribute"""
        # Add attributes to set
        attribute_set = AttributeSets(
            name="Test Attribute Set 1",
            attributes=[self.test_attribute1, self.test_attribute2]
        )
        await save_object(db_session, attribute_set)
        await db_session.refresh(attribute_set, ['attributes'])
        assert len(attribute_set.attributes) == 2

        # Remove all attributes from the set
        await delete_object(db_session, self.test_attribute1)
        await delete_object(db_session, self.test_attribute2)
        await db_session.refresh(attribute_set, ['attributes'])
        assert len(attribute_set.attributes) == 0

    @pytest.mark.asyncio
    async def test_setting_attribute_to_empty_list(
        self, db_session: AsyncSession
    ):
        """Test setting attributes to empty list"""
        attribute_set = AttributeSets(
            name="Test Attribute Set 1",
            attributes=[self.test_attribute1, self.test_attribute2]
        )
        await save_object(db_session, attribute_set)
        await db_session.refresh(attribute_set, ['attributes'])
        assert len(attribute_set.attributes) == 2

        attribute_set.attributes = []
        await save_object(db_session, attribute_set)
        await db_session.refresh(attribute_set, ['attributes'])
        assert len(attribute_set.attributes) == 0

    @pytest.mark.asyncio
    async def test_query_attribute_by_set(
        self, db_session: AsyncSession
    ):
        """Test querying attributes by their set"""
        # Associate attributes with sets
        attribute_set1 = AttributeSets(
            name="Test Attribute Set 1",
            attributes=[self.test_attribute1, self.test_attribute2]
        )
        await save_object(db_session, attribute_set1)

        attribute_set2 = AttributeSets(
            name="Test Attribute Set 2",
            attributes=[self.test_attribute1, self.test_attribute2]
        )
        await save_object(db_session, attribute_set2)

        # Query attributes by set
        stmt = select(Attributes).join(Attributes.attribute_sets).where(
            AttributeSets.name == "Test Attribute Set 1"
        )
        result = await db_session.execute(stmt)
        attributes = result.scalars().all()
        assert len(attributes) == 2
        assert self.test_attribute1 in attributes
        assert self.test_attribute2 in attributes

    """
    belum selesai
    """
