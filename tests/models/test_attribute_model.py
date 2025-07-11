from sqlalchemy import String, event, Enum as SAEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select
import pytest
from datetime import datetime

from app.core.base import Base
from app.models.attribute_model import Attributes, DataType
from app.models.attribute_set_model import AttributeSets
from app.models.sku_attribute_value_model import SkuAttributeValue
from app.core.listeners import _set_code
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    count_model_objects,
    assert_relationship
)


@pytest.fixture
async def setup_attributes(attribute_factory):
    """Fixture to create attributes for the test suite"""
    attribute1 = await attribute_factory(name="Test Attribute 1", uom="Test UOM 1")
    attribute2 = await attribute_factory(name="Test Attribute 2")
    return attribute1, attribute2


class TestAttribute:
    """Test suite for Attribute model"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_attributes):
        """Setup method for the test suite"""
        self.test_attribute1, self.test_attribute2 = setup_attributes

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
        assert str_repr == "Attributes(Test Attribute 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        await db_session.refresh(self.test_attribute1, ['sku_attribute_values'])
        await db_session.refresh(self.test_attribute1, ['attribute_sets'])

        await db_session.refresh(self.test_attribute2, ['sku_attribute_values'])
        await db_session.refresh(self.test_attribute2, ['attribute_sets'])

        assert self.test_attribute1.id == 1
        assert self.test_attribute1.name == "Test Attribute 1"
        assert self.test_attribute1.code == "TEST-ATTRIBUTE-1"
        assert self.test_attribute1.data_type == DataType.TEXT
        assert self.test_attribute1.uom == "Test UOM 1"
        assert self.test_attribute1.sku_attribute_values == []
        assert self.test_attribute1.attribute_sets == []

        assert self.test_attribute2.id == 2
        assert self.test_attribute2.name == "Test Attribute 2"
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
        assert item.name == "Test Attribute 1"
        assert item.code == "TEST-ATTRIBUTE-1"
        assert item.data_type == DataType.TEXT
        assert item.uom == "Test UOM 1"

        item = await get_object_by_id(db_session, Attributes, self.test_attribute2.id)
        assert item.id == 2
        assert item.name == "Test Attribute 2"
        assert item.code == "TEST-ATTRIBUTE-2"
        assert item.data_type == DataType.TEXT
        assert item.uom is None

        items = await get_all_objects(db_session, Attributes)
        assert len(items) == 2
        assert items[0].name == "Test Attribute 1"
        assert items[0].code == "TEST-ATTRIBUTE-1"
        assert items[0].data_type == DataType.TEXT
        assert items[0].uom == "Test UOM 1"
        assert items[1].name == "Test Attribute 2"
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


class TestAttributeAttributeSetRelationship:
    """Test suite for Attribute model relationships with AttributeSet model"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_attributes):
        """Setup method for the test suite"""
        self.test_attribute1, self.test_attribute2 = setup_attributes

    @pytest.mark.asyncio
    async def test_create_attribute_with_attribute_sets(self, db_session: AsyncSession):
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
        for i in range(5):
            attribute_set = AttributeSets(
                name=f"Test Attribute Set {i}",
                attributes=[self.test_attribute1]
            )
            await save_object(db_session, attribute_set)

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
    async def test_update_attributes_attribute_sets(self, db_session: AsyncSession):
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
    async def test_attribute_deletion_with_attribute_sets(
        self, db_session: AsyncSession
    ):
        """Test deleting an attribute from a set without deleting the attribute"""
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

        test_attribute1 = await get_object_by_id(
            db_session,
            Attributes,
            self.test_attribute1.id
        )
        test_attribute2 = await get_object_by_id(
            db_session,
            Attributes,
            self.test_attribute2.id
        )

        assert test_attribute1 is None
        assert test_attribute2 is None

    @pytest.mark.asyncio
    async def test_setting_attribute_attribute_sets_to_empty_list(
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

        test_attribute1 = await get_object_by_id(
            db_session,
            Attributes,
            self.test_attribute1.id
        )
        test_attribute2 = await get_object_by_id(
            db_session,
            Attributes,
            self.test_attribute2.id
        )

        assert test_attribute1 is not None
        assert test_attribute2 is not None

    @pytest.mark.asyncio
    async def test_query_attribute_by_attribute_set(self, db_session: AsyncSession):
        """Test querying attributes by their attribute sets"""
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

        # Query attributes by attribute set
        stmt = select(Attributes).join(Attributes.attribute_sets).where(
            AttributeSets.name == "Test Attribute Set 1"
        )
        result = await db_session.execute(stmt)
        attributes = result.scalars().all()
        assert len(attributes) == 2
        assert self.test_attribute1 in attributes
        assert self.test_attribute2 in attributes


class TestAttributeSkuAttributeValueRelationship:
    """Test suite for Attribute model relationships with SkuAttributeValue model"""

    @pytest.fixture(autouse=True)
    async def setup_objects(self, setup_attributes, sku_factory):
        """Setup method for the test suite"""
        self.test_attribute1, self.test_attribute2 = setup_attributes
        self.test_sku1 = await sku_factory(name="Test SKU 1")
        self.test_sku2 = await sku_factory(name="Test SKU 2")

    @pytest.mark.asyncio
    async def test_create_attribute_with_sku_attribute_values(
        self, db_session: AsyncSession
    ):
        """Test creating an attribute and associating it with multiple sku attribute
        values
        """
        attribute = Attributes(
            name="Test Attribute with Sku Attribute Values",
            sku_attribute_values=[
                SkuAttributeValue(
                    value="Test Sku Attribute Value 1",
                    sku_id=self.test_sku1.id
                ),
                SkuAttributeValue(
                    value="Test Sku Attribute Value 2",
                    sku_id=self.test_sku2.id
                )
            ]
        )
        await save_object(db_session, attribute)

        retrieved_attribute = await get_object_by_id(
            db_session,
            Attributes,
            attribute.id
        )
        await db_session.refresh(retrieved_attribute, ['sku_attribute_values'])

        assert retrieved_attribute.id == 3
        assert retrieved_attribute.name == "Test Attribute with Sku Attribute Values"
        assert len(retrieved_attribute.sku_attribute_values) == 2
        assert retrieved_attribute.sku_attribute_values[0].value == (
            "Test Sku Attribute Value 1"
        )
        assert retrieved_attribute.sku_attribute_values[1].value == (
            "Test Sku Attribute Value 2"
        )

    @pytest.mark.asyncio
    async def test_add_multiple_sku_attribute_values_to_attribute(
        self, db_session: AsyncSession
    ):
        """Test adding multiple sku attribute values to an attribute"""
        sku_id = self.test_sku1.id
        attribute_id = self.test_attribute1.id
        for i in range(5):
            sku_attribute_value = SkuAttributeValue(
                value=f"Test Sku Attribute Value {i}",
                sku_id=sku_id,
                attribute_id=attribute_id
            )

            if i >= 1:
                # should fail because sku_id and attribute_id are no longer unique
                with pytest.raises(IntegrityError):
                    await save_object(db_session, sku_attribute_value)
                await db_session.rollback()
            else:
                await save_object(db_session, sku_attribute_value)

    @pytest.mark.asyncio
    async def test_update_attributes_sku_attribute_values(
        self, db_session: AsyncSession
    ):
        """Test updating an attribute's sku attribute values"""
        attribute = await get_object_by_id(
            db_session,
            Attributes,
            self.test_attribute1.id
        )
        await db_session.refresh(attribute, ['sku_attribute_values'])
        assert len(attribute.sku_attribute_values) == 0

        attribute.sku_attribute_values = [
            SkuAttributeValue(
                value="Test Sku Attribute Value 1",
                sku_id=self.test_sku1.id
            ),
            SkuAttributeValue(
                value="Test Sku Attribute Value 2",
                sku_id=self.test_sku2.id
            )
        ]
        await save_object(db_session, attribute)
        await db_session.refresh(attribute, ['sku_attribute_values'])
        assert len(attribute.sku_attribute_values) == 2
        assert attribute.sku_attribute_values[0].value == "Test Sku Attribute Value 1"
        assert attribute.sku_attribute_values[1].value == "Test Sku Attribute Value 2"

        attribute.sku_attribute_values = [
            SkuAttributeValue(
                value="Test Sku Attribute Value 3",
                sku_id=self.test_sku1.id
            )
        ]
        with pytest.raises(IntegrityError):
            # should fail because Test Sku Attribute Value 1 and Test Sku Attribute
            # Value 2 no longer have attribute_id
            await save_object(db_session, attribute)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_attribute_deletion_with_sku_attribute_values(
        self, db_session: AsyncSession
    ):
        """Test deleting an attribute from a sku without deleting the attribute"""
        sku_attribute_value = SkuAttributeValue(
            value="Test Sku Attribute Value 1",
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute1.id
        )
        await save_object(db_session, sku_attribute_value)
        await db_session.refresh(sku_attribute_value, ['attribute'])
        assert sku_attribute_value.attribute_id == self.test_attribute1.id

        # should fail because sku_attribute_value will lose its attribute_id
        with pytest.raises(IntegrityError):
            await delete_object(db_session, self.test_attribute1)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_orphaned_sku_attribute_value_cleanup(self, db_session: AsyncSession):
        """Test handling of sku attribute values when their attribute is deleted"""
        # Create a temporary attribute
        temp_attribute = Attributes(
            name="Temporary Attribute for SKU test",
        )
        await save_object(db_session, temp_attribute)

        temp_sku_attribute_value = SkuAttributeValue(
            value="Temporary Sku Attribute Value",
            sku_id=self.test_sku1.id,
            attribute_id=temp_attribute.id
        )
        await save_object(db_session, temp_sku_attribute_value)

        # Try to delete the attribute (should fail because of foreign key)
        with pytest.raises(IntegrityError):
            await delete_object(db_session, temp_attribute)
        await db_session.rollback()

        # To properly delete, first remove the sku attribute value
        await delete_object(db_session, temp_sku_attribute_value)
        await delete_object(db_session, temp_attribute)

        # Verify both are deleted
        deleted_attribute = await get_object_by_id(
            db_session,
            Attributes,
            temp_attribute.id
        )
        deleted_sku_attribute_value = await get_object_by_id(
            db_session,
            SkuAttributeValue,
            temp_sku_attribute_value.id
        )
        assert deleted_attribute is None
        assert deleted_sku_attribute_value is None

    @pytest.mark.asyncio
    async def test_query_attribute_by_sku_attribute_value(
        self, db_session: AsyncSession
    ):
        """Test querying attributes by their sku attribute values"""
        sku_attribute_value1 = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute1.id,
            value="Test Sku Attribute Value 1"
        )
        await save_object(db_session, sku_attribute_value1)

        sku_attribute_value2 = SkuAttributeValue(
            sku_id=self.test_sku2.id,
            attribute_id=self.test_attribute1.id,
            value="Test Sku Attribute Value 2"
        )
        await save_object(db_session, sku_attribute_value2)

        stmt = select(Attributes).join(Attributes.sku_attribute_values).where(
            SkuAttributeValue.value == "Test Sku Attribute Value 1"
        )
        result = await db_session.execute(stmt)
        attributes = result.scalars().all()
        assert len(attributes) == 1
        assert self.test_attribute1 in attributes


class TestAttributeStaticMethods:
    """Test suite for Attribute model static methods"""

    def test_validate_value_for_data_type_text(self):
        """Test validate_value_for_data_type with TEXT data type"""
        # Valid cases
        assert Attributes.validate_value_for_data_type("test", DataType.TEXT) is True
        assert Attributes.validate_value_for_data_type("123", DataType.TEXT) is True
        assert Attributes.validate_value_for_data_type("true", DataType.TEXT) is True
        assert Attributes.validate_value_for_data_type("2023-01-01", DataType.TEXT) is \
            True
        assert Attributes.validate_value_for_data_type("", DataType.TEXT) is True
        assert Attributes.validate_value_for_data_type("   ", DataType.TEXT) is True
        assert Attributes.validate_value_for_data_type(
            "Special chars: !@#$%^&*()",
            DataType.TEXT
        ) is True
        assert Attributes.validate_value_for_data_type("Unicode: 🚀", DataType.TEXT) is \
            True

    def test_validate_value_for_data_type_number(self):
        """Test validate_value_for_data_type with NUMBER data type"""
        # Valid cases
        assert Attributes.validate_value_for_data_type(
            "123", DataType.NUMBER
        ) is True
        assert Attributes.validate_value_for_data_type(
            "123.45", DataType.NUMBER
        ) is True
        assert Attributes.validate_value_for_data_type(
            "-123", DataType.NUMBER
        ) is True
        assert Attributes.validate_value_for_data_type(
            "-123.45", DataType.NUMBER
        ) is True
        assert Attributes.validate_value_for_data_type(
            "0", DataType.NUMBER
        ) is True
        assert Attributes.validate_value_for_data_type(
            "0.0", DataType.NUMBER
        ) is True
        assert Attributes.validate_value_for_data_type(
            "1e5", DataType.NUMBER
        ) is True
        assert Attributes.validate_value_for_data_type(
            "1.5e-10", DataType.NUMBER
        ) is True

        # Invalid cases
        assert Attributes.validate_value_for_data_type(
            "abc", DataType.NUMBER
        ) is False
        assert Attributes.validate_value_for_data_type(
            "123abc", DataType.NUMBER
        ) is False
        assert Attributes.validate_value_for_data_type(
            "12.34.56", DataType.NUMBER
        ) is False
        assert Attributes.validate_value_for_data_type(
            "--123", DataType.NUMBER
        ) is False
        assert Attributes.validate_value_for_data_type(
            "12..34", DataType.NUMBER
        ) is False

    def test_validate_value_for_data_type_boolean(self):
        """Test validate_value_for_data_type with BOOLEAN data type"""
        # Valid cases
        assert Attributes.validate_value_for_data_type(
            "true", DataType.BOOLEAN
        ) is True
        assert Attributes.validate_value_for_data_type(
            "false", DataType.BOOLEAN
        ) is True
        assert Attributes.validate_value_for_data_type(
            "TRUE", DataType.BOOLEAN
        ) is True
        assert Attributes.validate_value_for_data_type(
            "FALSE", DataType.BOOLEAN
        ) is True
        assert Attributes.validate_value_for_data_type(
            "True", DataType.BOOLEAN
        ) is True
        assert Attributes.validate_value_for_data_type(
            "False", DataType.BOOLEAN
        ) is True
        assert Attributes.validate_value_for_data_type(
            "  true  ", DataType.BOOLEAN
        ) is True
        assert Attributes.validate_value_for_data_type(
            "  false  ", DataType.BOOLEAN
        ) is True

        # Invalid cases
        assert Attributes.validate_value_for_data_type(
            "yes", DataType.BOOLEAN
        ) is False
        assert Attributes.validate_value_for_data_type(
            "no", DataType.BOOLEAN
        ) is False
        assert Attributes.validate_value_for_data_type(
            "1", DataType.BOOLEAN
        ) is False
        assert Attributes.validate_value_for_data_type(
            "0", DataType.BOOLEAN
        ) is False
        assert Attributes.validate_value_for_data_type(
            "True1", DataType.BOOLEAN
        ) is False
        assert Attributes.validate_value_for_data_type(
            "abc", DataType.BOOLEAN
        ) is False

    def test_validate_value_for_data_type_date(self):
        """Test validate_value_for_data_type with DATE data type"""
        # Valid cases
        assert Attributes.validate_value_for_data_type(
            "2023-01-01", DataType.DATE
        ) is True
        assert Attributes.validate_value_for_data_type(
            "2023-12-31", DataType.DATE
        ) is True
        assert Attributes.validate_value_for_data_type(
            "2023-01-01T10:30:00", DataType.DATE
        ) is True
        assert Attributes.validate_value_for_data_type(
            "2023-01-01T10:30:00.123456", DataType.DATE
        ) is True
        assert Attributes.validate_value_for_data_type(
            "2023-01-01T10:30:00+05:30", DataType.DATE
        ) is True
        assert Attributes.validate_value_for_data_type(
            "2023-01-01T10:30:00Z", DataType.DATE
        ) is True
        assert Attributes.validate_value_for_data_type(
            "2023-01-01T10:30:00.123456Z", DataType.DATE
        ) is True

        # Invalid cases
        assert Attributes.validate_value_for_data_type(
            "2023-13-01", DataType.DATE
        ) is False
        assert Attributes.validate_value_for_data_type(
            "2023-01-32", DataType.DATE
        ) is False
        assert Attributes.validate_value_for_data_type(
            "23-01-01", DataType.DATE
        ) is False
        assert Attributes.validate_value_for_data_type(
            "2023/01/01", DataType.DATE
        ) is False
        assert Attributes.validate_value_for_data_type(
            "01-01-2023", DataType.DATE
        ) is False
        assert Attributes.validate_value_for_data_type(
            "abc", DataType.DATE
        ) is False
        assert Attributes.validate_value_for_data_type(
            "2023-01-01T25:00:00", DataType.DATE
        ) is False

    def test_validate_value_for_data_type_edge_cases(self):
        """Test validate_value_for_data_type with edge cases (empty, None)"""
        test_cases = [
            ("", DataType.TEXT),
            ("", DataType.NUMBER),
            ("", DataType.BOOLEAN),
            ("", DataType.DATE),
            (None, DataType.TEXT),
            (None, DataType.NUMBER),
            (None, DataType.BOOLEAN),
            (None, DataType.DATE),
        ]

        for value, data_type in test_cases:
            assert Attributes.validate_value_for_data_type(
                value, data_type
            ) is True, f"Failed for value={value}, data_type={data_type}"

    def test_convert_value_to_python_text(self):
        """Test convert_value_to_python with TEXT data type"""
        assert Attributes.convert_value_to_python("test", DataType.TEXT) == "test"
        assert Attributes.convert_value_to_python("123", DataType.TEXT) == "123"
        assert Attributes.convert_value_to_python("true", DataType.TEXT) == "true"
        assert Attributes.convert_value_to_python(
            "2023-01-01", DataType.TEXT
        ) == "2023-01-01"
        assert Attributes.convert_value_to_python("   ", DataType.TEXT) == "   "
        assert Attributes.convert_value_to_python(
            "Special chars: !@#$%^&*()", DataType.TEXT
        ) == "Special chars: !@#$%^&*()"

    def test_convert_value_to_python_number(self):
        """Test convert_value_to_python with NUMBER data type"""
        # Valid cases
        assert Attributes.convert_value_to_python(
            "123", DataType.NUMBER
        ) == 123.0
        assert Attributes.convert_value_to_python(
            "123.45", DataType.NUMBER
        ) == 123.45
        assert Attributes.convert_value_to_python(
            "-123", DataType.NUMBER
        ) == -123.0
        assert Attributes.convert_value_to_python(
            "-123.45", DataType.NUMBER
        ) == -123.45
        assert Attributes.convert_value_to_python(
            "0", DataType.NUMBER
        ) == 0.0
        assert Attributes.convert_value_to_python(
            "0.0", DataType.NUMBER
        ) == 0.0
        assert Attributes.convert_value_to_python(
            "1e5", DataType.NUMBER
        ) == 100000.0
        assert Attributes.convert_value_to_python(
            "1.5e-10", DataType.NUMBER
        ) == 1.5e-10

    def test_convert_value_to_python_boolean(self):
        """Test convert_value_to_python with BOOLEAN data type"""
        # Valid true cases
        assert Attributes.convert_value_to_python(
            "true", DataType.BOOLEAN
        ) is True
        assert Attributes.convert_value_to_python(
            "TRUE", DataType.BOOLEAN
        ) is True
        assert Attributes.convert_value_to_python(
            "True", DataType.BOOLEAN
        ) is True
        assert Attributes.convert_value_to_python(
            "  true  ", DataType.BOOLEAN
        ) is True

        # Valid false cases
        assert Attributes.convert_value_to_python(
            "false", DataType.BOOLEAN
        ) is False
        assert Attributes.convert_value_to_python(
            "FALSE", DataType.BOOLEAN
        ) is False
        assert Attributes.convert_value_to_python(
            "False", DataType.BOOLEAN
        ) is False
        assert Attributes.convert_value_to_python(
            "  false  ", DataType.BOOLEAN
        ) is False

    def test_convert_value_to_python_date(self):
        """Test convert_value_to_python with DATE data type"""
        # Valid cases
        result = Attributes.convert_value_to_python(
            "2023-01-01", DataType.DATE
        )
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 1

        result = Attributes.convert_value_to_python(
            "2023-12-31T23:59:59", DataType.DATE
        )
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 31
        assert result.hour == 23
        assert result.minute == 59
        assert result.second == 59

        result = Attributes.convert_value_to_python(
            "2023-01-01T10:30:00.123456", DataType.DATE
        )
        assert isinstance(result, datetime)
        assert result.microsecond == 123456

        # Test timezone handling
        result = Attributes.convert_value_to_python(
            "2023-01-01T10:30:00Z", DataType.DATE
        )
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

        result = Attributes.convert_value_to_python(
            "2023-01-01T10:30:00+05:30", DataType.DATE
        )
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_convert_value_to_python_edge_cases(self):
        """Test convert_value_to_python with edge cases (empty, None)"""
        # Test with all data types and edge values
        test_cases = [
            ("", DataType.TEXT, None),
            ("", DataType.NUMBER, None),
            ("", DataType.BOOLEAN, None),
            ("", DataType.DATE, None),
            (None, DataType.TEXT, None),
            (None, DataType.NUMBER, None),
            (None, DataType.BOOLEAN, None),
            (None, DataType.DATE, None),
        ]

        for value, data_type, expected in test_cases:
            result = Attributes.convert_value_to_python(value, data_type)
            assert result == expected, (
                f"Failed for value={value}, data_type={data_type}"
            )

    def test_static_methods_integration(self):
        """
        Test integration between validate_value_for_data_type and
        convert_value_to_python
        """
        test_cases = [
            ("123", DataType.NUMBER),
            ("true", DataType.BOOLEAN),
            ("2023-01-01", DataType.DATE),
            ("test", DataType.TEXT),
        ]

        for value, data_type in test_cases:
            # If validation passes, conversion should work
            is_valid = Attributes.validate_value_for_data_type(value, data_type)
            assert is_valid is True

            # Conversion should not raise exception
            converted = Attributes.convert_value_to_python(value, data_type)
            assert converted is not None

            # For TEXT type, value should remain the same
            if data_type == DataType.TEXT:
                assert converted == value
            # For NUMBER type, should be float
            elif data_type == DataType.NUMBER:
                assert isinstance(converted, float)
            # For BOOLEAN type, should be bool
            elif data_type == DataType.BOOLEAN:
                assert isinstance(converted, bool)
            # For DATE type, should be datetime
            elif data_type == DataType.DATE:
                assert isinstance(converted, datetime)
