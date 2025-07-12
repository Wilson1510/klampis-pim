from sqlalchemy import String, Integer, UniqueConstraint, Index
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from app.models.sku_attribute_value_model import SkuAttributeValue
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    assert_relationship,
    count_model_objects
)


@pytest.fixture
async def setup_sku_attribute_values(
    sku_attribute_value_factory, sku_factory, attribute_factory
):
    """Fixture to create sku attribute values for the test suite"""
    test_sku1 = await sku_factory(name="Test Sku 1")
    test_sku2 = await sku_factory(name="Test Sku 2")
    test_attribute1 = await attribute_factory(
        name="Test Attribute 1",
        data_type="TEXT"
    )
    test_attribute2 = await attribute_factory(
        name="Test Attribute 2",
        data_type="NUMBER"
    )

    test_sku_attr_value1 = await sku_attribute_value_factory(
        sku_id=test_sku1.id,
        attribute_id=test_attribute1.id,
        value="Test Value 1"
    )
    test_sku_attr_value2 = await sku_attribute_value_factory(
        sku_id=test_sku2.id,
        attribute_id=test_attribute2.id,
        value="123"
    )

    return (
        test_sku1, test_sku2, test_attribute1, test_attribute2,
        test_sku_attr_value1, test_sku_attr_value2
    )


class TestSkuAttributeValue:
    """Test suite for SkuAttributeValue model and relationships"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_sku_attribute_values):
        """Setup method for the test suite"""
        (
            self.test_sku1, self.test_sku2, self.test_attribute1,
            self.test_attribute2, self.test_sku_attr_value1, self.test_sku_attr_value2
        ) = setup_sku_attribute_values

    def test_inheritance_from_base_model(self):
        """Test that SkuAttributeValue model inherits from Base model"""
        assert issubclass(SkuAttributeValue, Base)

    def test_fields_with_validation(self):
        """Test that SkuAttributeValue model has fields with validation"""
        assert hasattr(SkuAttributeValue, 'validate_value')
        assert not hasattr(SkuAttributeValue, 'validate_sku_id')
        assert len(SkuAttributeValue.__mapper__.validators) == 1

    def test_table_args(self):
        """Test that the table has the expected table args"""
        table_args = SkuAttributeValue.__table_args__

        # Check that we have exactly 2 constraints
        assert len(table_args) == 2

        # Check constraint types and names
        unique_constraint = table_args[0]
        composite_index = table_args[1]

        assert isinstance(unique_constraint, UniqueConstraint)
        assert isinstance(composite_index, Index)

        assert unique_constraint.name == 'uq_sku_attribute'
        assert composite_index.name == 'idx_sku_attribute_composite'

        # Check unique constraint columns
        assert set(unique_constraint.columns.keys()) == {'sku_id', 'attribute_id'}

        # Check composite index columns
        index_columns = set(col.name for col in composite_index.columns)
        assert index_columns == {'sku_id', 'attribute_id'}

        assert not hasattr(unique_constraint, 'sqltext')
        assert not hasattr(composite_index, 'sqltext')

    def test_sku_id_field_properties(self):
        """Test the properties of the sku_id field"""
        sku_id_column = SkuAttributeValue.__table__.columns.get('sku_id')
        assert sku_id_column is not None
        assert isinstance(sku_id_column.type, Integer)
        assert sku_id_column.nullable is False
        foreign_key = list(sku_id_column.foreign_keys)[0]
        assert str(foreign_key.target_fullname) == "skus.id"
        assert sku_id_column.unique is None
        assert sku_id_column.index is True
        assert sku_id_column.default is None

    def test_attribute_id_field_properties(self):
        """Test the properties of the attribute_id field"""
        attribute_id_column = SkuAttributeValue.__table__.columns.get('attribute_id')
        assert attribute_id_column is not None
        assert isinstance(attribute_id_column.type, Integer)
        assert attribute_id_column.nullable is False
        foreign_key = list(attribute_id_column.foreign_keys)[0]
        assert str(foreign_key.target_fullname) == "attributes.id"
        assert attribute_id_column.unique is None
        assert attribute_id_column.index is True
        assert attribute_id_column.default is None

    def test_value_field_properties(self):
        """Test the properties of the value field"""
        value_column = SkuAttributeValue.__table__.columns.get('value')
        assert value_column is not None
        assert isinstance(value_column.type, String)
        assert value_column.type.length == 50
        assert value_column.nullable is False
        assert value_column.unique is None
        assert value_column.index is True
        assert value_column.default is None

    def test_relationships_with_other_models(self):
        """Test the relationships with other models"""
        assert_relationship(SkuAttributeValue, "sku", "sku_attribute_values")
        assert_relationship(SkuAttributeValue, "attribute", "sku_attribute_values")

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_sku_attr_value1)
        expected = (
            f"SkuAttributeValue(sku:{self.test_sku1.id}, "
            f"attribute:{self.test_attribute1.id}, value:Test Value 1)"
        )
        assert str_repr == expected

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        assert self.test_sku_attr_value1.id == 1
        assert self.test_sku_attr_value1.sku_id == self.test_sku1.id
        assert self.test_sku_attr_value1.attribute_id == self.test_attribute1.id
        assert self.test_sku_attr_value1.value == "Test Value 1"

        assert self.test_sku_attr_value2.id == 2
        assert self.test_sku_attr_value2.sku_id == self.test_sku2.id
        assert self.test_sku_attr_value2.attribute_id == self.test_attribute2.id
        assert self.test_sku_attr_value2.value == "123"

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute2.id,
            value="456"
        )
        await save_object(db_session, item)

        assert item.id == 3
        assert item.sku_id == self.test_sku1.id
        assert item.attribute_id == self.test_attribute2.id
        assert item.value == "456"
        assert await count_model_objects(db_session, SkuAttributeValue) == 3

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(
            db_session,
            SkuAttributeValue,
            self.test_sku_attr_value1.id
        )
        assert item.id == 1
        assert item.sku_id == self.test_sku1.id
        assert item.attribute_id == self.test_attribute1.id
        assert item.value == "Test Value 1"

        item = await get_object_by_id(
            db_session,
            SkuAttributeValue,
            self.test_sku_attr_value2.id
        )
        assert item.id == 2
        assert item.sku_id == self.test_sku2.id
        assert item.attribute_id == self.test_attribute2.id
        assert item.value == "123"

        items = await get_all_objects(db_session, SkuAttributeValue)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].sku_id == self.test_sku1.id
        assert items[0].attribute_id == self.test_attribute1.id
        assert items[0].value == "Test Value 1"

        assert items[1].id == 2
        assert items[1].sku_id == self.test_sku2.id
        assert items[1].attribute_id == self.test_attribute2.id
        assert items[1].value == "123"

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(
            db_session,
            SkuAttributeValue,
            self.test_sku_attr_value1.id
        )

        item.value = "Updated Test Value"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.sku_id == self.test_sku1.id
        assert item.attribute_id == self.test_attribute1.id
        assert item.value == "Updated Test Value"
        assert await count_model_objects(db_session, SkuAttributeValue) == 2

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_sku_attr_value2)

        item = await get_object_by_id(
            db_session,
            SkuAttributeValue,
            self.test_sku_attr_value2.id
        )
        assert item is None
        assert await count_model_objects(db_session, SkuAttributeValue) == 1


class TestSkuAttributeValueConstraint:
    pass


class TestSkuAttributeValueValidation:
    pass


class TestSkuAttributeValueSkuRelationship:
    pass


class TestSkuAttributeValueAttributeRelationship:
    pass


class TestSkuAttributeValueMethods:
    pass
