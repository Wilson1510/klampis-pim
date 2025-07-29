from sqlalchemy import (
    String, Integer, UniqueConstraint, Index, text, select, CheckConstraint
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import pytest

from app.core.base import Base
from app.models import Attributes, Skus, SkuAttributeValue
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
        assert len(table_args) == 3

        # Check constraint types and names
        unique_constraint = table_args[0]
        composite_index = table_args[1]
        check_constraint = table_args[2]

        assert isinstance(unique_constraint, UniqueConstraint)
        assert isinstance(composite_index, Index)
        assert isinstance(check_constraint, CheckConstraint)

        assert unique_constraint.name == 'uq_sku_attribute'
        assert composite_index.name == 'idx_sku_attribute_composite'
        assert check_constraint.name == 'check_sku_attribute_value_value_not_empty'

        # Check unique constraint columns
        assert set(unique_constraint.columns.keys()) == {'sku_id', 'attribute_id'}

        # Check composite index columns
        index_columns = set(col.name for col in composite_index.columns)
        assert index_columns == {'sku_id', 'attribute_id'}

        # Check check constraint SQL text
        assert str(check_constraint.sqltext) == "LENGTH(TRIM(value)) > 0"

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


class TestSkuAttributeValueValidationDatabase:
    """Test suite for SkuAttributeValue model constraints"""

    @pytest.fixture(autouse=True)
    async def setup_objects(
        self, setup_sku_attribute_values, sku_factory, attribute_factory
    ):
        """Setup method for the test suite"""
        (
            self.test_sku1, self.test_sku2, self.test_attribute1,
            self.test_attribute2, self.test_sku_attr_value1, self.test_sku_attr_value2
        ) = setup_sku_attribute_values
        self.another_sku = await sku_factory(name="Another SKU")
        self.another_attribute = await attribute_factory(name="Another Attribute")

    @pytest.mark.asyncio
    async def test_create_item_same_objects_sku_id_and_attribute_id(
        self, db_session: AsyncSession
    ):
        """
        Test that creating an item with the same combination of sku_id and attribute_id
        belonging to an item fails.
        """
        duplicate_sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku_attr_value1.sku_id,
            attribute_id=self.test_sku_attr_value1.attribute_id,
            value="Same Existing Sku and Attribute"
        )

        with pytest.raises(IntegrityError):
            await save_object(db_session, duplicate_sku_attribute_value)

        await db_session.rollback()

        assert await count_model_objects(db_session, SkuAttributeValue) == 2

    @pytest.mark.asyncio
    async def test_update_item_same_objects_sku_id_and_attribute_id(
        self, db_session: AsyncSession
    ):
        """
        Test that updating an item with the same combination of sku_id and attribute_id
        belonging to an item fails.
        """
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.another_sku.id,
            attribute_id=self.another_attribute.id,
            value="Updated Sku and Attribute"
        )

        await save_object(db_session, sku_attribute_value)

        assert sku_attribute_value.sku_id == self.another_sku.id
        assert sku_attribute_value.sku == self.another_sku
        assert sku_attribute_value.sku.name == "Another SKU"
        assert sku_attribute_value.attribute_id == self.another_attribute.id
        assert sku_attribute_value.attribute == self.another_attribute
        assert sku_attribute_value.attribute.name == "Another Attribute"

        sku_attribute_value.sku_id = self.test_sku1.id
        sku_attribute_value.attribute_id = self.test_attribute1.id
        with pytest.raises(IntegrityError):
            await save_object(db_session, sku_attribute_value)

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_create_item_different_objects_sku_id_and_attribute_id(
        self, db_session: AsyncSession
    ):
        """
        Test that creating an item with a different sku_id and attribute_id belonging to
        an item succeeds.
        """
        new_sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku_attr_value1.sku_id,
            attribute_id=self.test_attribute2.id,
            value="Different Existing Sku and Attribute"
        )

        await save_object(db_session, new_sku_attribute_value)

        assert await count_model_objects(db_session, SkuAttributeValue) == 3

    @pytest.mark.asyncio
    async def test_update_item_different_objects_sku_id_and_attribute_id(
        self, db_session: AsyncSession
    ):
        """
        Test that updating an item with a different sku_id and attribute_id belonging to
        an item succeeds.
        """
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.another_sku.id,
            attribute_id=self.another_attribute.id,
            value="Updated Sku and Attribute"
        )

        await save_object(db_session, sku_attribute_value)

        sku_attribute_value.sku_id = self.test_sku1.id
        sku_attribute_value.attribute_id = self.test_attribute2.id
        await save_object(db_session, sku_attribute_value)

        assert sku_attribute_value.sku_id == self.test_sku1.id
        assert sku_attribute_value.sku == self.test_sku1
        assert sku_attribute_value.sku.name == "Test Sku 1"
        assert sku_attribute_value.attribute_id == self.test_attribute2.id
        assert sku_attribute_value.attribute == self.test_attribute2
        assert sku_attribute_value.attribute.name == "Test Attribute 2"

    @pytest.mark.asyncio
    async def test_create_item_objects_sku_id_and_new_attribute_id(
        self, db_session: AsyncSession, attribute_factory
    ):
        """
        Test that creating an item with an existing sku_id belonging to an item and a
        attribute_id not belonging to an item succeeds.
        """
        new_attribute = await attribute_factory(
            name="New Attribute",
            data_type="TEXT"
        )
        new_sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku_attr_value1.sku_id,
            attribute_id=new_attribute.id,
            value="New Sku and Attribute"
        )

        await save_object(db_session, new_sku_attribute_value)

        assert await count_model_objects(db_session, SkuAttributeValue) == 3

    @pytest.mark.asyncio
    async def test_update_item_objects_sku_id_and_new_attribute_id(
        self, db_session: AsyncSession, attribute_factory
    ):
        """
        Test that updating an item with an existing sku_id belonging to an item and a
        attribute_id not belonging to an item succeeds.
        """
        new_attribute = await attribute_factory(
            name="New Attribute",
            data_type="TEXT"
        )
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.another_sku.id,
            attribute_id=self.another_attribute.id,
            value="Updated Sku and Attribute"
        )

        await save_object(db_session, sku_attribute_value)

        sku_attribute_value.sku_id = self.test_sku1.id
        sku_attribute_value.attribute_id = new_attribute.id
        await save_object(db_session, sku_attribute_value)

        assert sku_attribute_value.sku_id == self.test_sku1.id
        assert sku_attribute_value.sku == self.test_sku1
        assert sku_attribute_value.sku.name == "Test Sku 1"
        assert sku_attribute_value.attribute_id == new_attribute.id
        assert sku_attribute_value.attribute == new_attribute
        assert sku_attribute_value.attribute.name == "New Attribute"

    @pytest.mark.asyncio
    async def test_create_item_objects_new_sku_id_and_objects_attribute_id(
        self, db_session: AsyncSession, sku_factory
    ):
        """
        Test that creating an item with a new sku_id and attribute_id belonging to an
        item succeeds.
        """
        new_sku = await sku_factory(name="New Sku")

        new_sku_attribute_value = SkuAttributeValue(
            sku_id=new_sku.id,
            attribute_id=self.test_attribute2.id,
            value="New Sku and Attribute"
        )

        await save_object(db_session, new_sku_attribute_value)

        assert await count_model_objects(db_session, SkuAttributeValue) == 3

    @pytest.mark.asyncio
    async def test_update_item_objects_new_sku_id_and_objects_attribute_id(
        self, db_session: AsyncSession, sku_factory
    ):
        """
        Test that updating an item with a new sku_id and attribute_id belonging to an
        item succeeds.
        """
        new_sku = await sku_factory(name="New Sku")

        sku_attribute_value = SkuAttributeValue(
            sku_id=self.another_sku.id,
            attribute_id=self.another_attribute.id,
            value="Updated Sku and Attribute"
        )

        await save_object(db_session, sku_attribute_value)

        sku_attribute_value.sku_id = new_sku.id
        sku_attribute_value.attribute_id = self.test_attribute1.id
        await save_object(db_session, sku_attribute_value)

        assert sku_attribute_value.sku_id == new_sku.id
        assert sku_attribute_value.sku == new_sku
        assert sku_attribute_value.sku.name == "New Sku"
        assert sku_attribute_value.attribute_id == self.test_attribute1.id
        assert sku_attribute_value.attribute == self.test_attribute1
        assert sku_attribute_value.attribute.name == "Test Attribute 1"

    @pytest.mark.asyncio
    async def test_create_item_not_empty_value(
        self, db_session: AsyncSession, attribute_factory
    ):
        """
        Test that creating an item with an empty value fails.
        """
        non_empty_value = ["Another Value", "  Another Value 1  ", "Another Value 2 "]
        for index, value in enumerate(non_empty_value, 3):
            attribute = await attribute_factory(name=f"Test Attribute {index}")
            sql = text("""
                INSERT INTO sku_attribute_value (
                       sku_id,
                       attribute_id,
                       value,
                       is_active,
                       sequence,
                       created_by,
                       updated_by
                )
                VALUES (
                       :sku_id,
                       :attribute_id,
                       :value,
                       :is_active,
                       :sequence,
                       :created_by,
                       :updated_by
                )
            """)

            await db_session.execute(sql, {
                'sku_id': self.test_sku1.id,
                'attribute_id': attribute.id,
                'value': value,
                'is_active': True,
                'sequence': 1,
                'created_by': 1,  # System user ID
                'updated_by': 1   # System user ID
            })
            await db_session.commit()

            stmt = select(SkuAttributeValue).where(SkuAttributeValue.value == value)
            result = await db_session.execute(stmt)
            sku_attribute_value = result.scalar_one_or_none()
            assert sku_attribute_value.value == value

    @pytest.mark.asyncio
    async def test_create_item_empty_value(self, db_session: AsyncSession):
        """
        Test that creating an item with an empty value fails.
        """
        empty_value = ["", "   "]
        sku_id = self.test_sku1.id
        attribute_id = self.test_attribute2.id
        for value in empty_value:
            # Use raw SQL to bypass application validation and test database constraint
            sql = text("""
                INSERT INTO sku_attribute_value (
                       sku_id,
                       attribute_id,
                       value,
                       is_active,
                       sequence,
                       created_by,
                       updated_by
                )
                VALUES (
                       :sku_id,
                       :attribute_id,
                       :value,
                       :is_active,
                       :sequence,
                       :created_by,
                       :updated_by
                )
            """)

            # This should fail at database level due to CheckConstraint
            with pytest.raises(
                IntegrityError, match="check_sku_attribute_value_value_not_empty"
            ):
                await db_session.execute(sql, {
                    'sku_id': sku_id,
                    'attribute_id': attribute_id,
                    'value': value,
                    'is_active': True,
                    'sequence': 1,
                    'created_by': 1,  # System user ID
                    'updated_by': 1   # System user ID
                })
            await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_item_empty_value(self, db_session: AsyncSession):
        """Test updating item with empty value fails database constraint"""
        # Create valid sku attribute value first
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        await save_object(db_session, sku_attribute_value)

        empty_value = ["", "   "]
        sku_attribute_value_id = sku_attribute_value.id

        # Try to update with invalid file name using raw SQL to bypass
        # application validation
        for value in empty_value:
            sql = text("""
                UPDATE sku_attribute_value
                SET value = :value
                WHERE id = :sku_attribute_value_id
            """)

            with pytest.raises(
                IntegrityError, match="check_sku_attribute_value_value_not_empty"
            ):
                await db_session.execute(sql, {
                    'value': value,
                    'sku_attribute_value_id': sku_attribute_value_id
                })
            await db_session.rollback()


class TestSkuAttributeValueValidationApplication:
    """Test suite for SkuAttributeValue model validation"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_sku_attribute_values):
        """Setup method for the test suite"""
        (
            self.test_sku1, self.test_sku2, self.test_attribute1,
            self.test_attribute2, self.test_sku_attr_value1, self.test_sku_attr_value2
        ) = setup_sku_attribute_values

    def test_non_empty_value(self):
        """Test that a non-empty value is allowed"""
        non_empty_value = ["Test Value", "  Test Value 1  ", "Test Value 2 "]
        for value in non_empty_value:
            sku_attribute_value = SkuAttributeValue(
                sku_id=self.test_sku1.id,
                attribute_id=self.test_attribute2.id,
                value=value
            )
            assert sku_attribute_value.value == value

    def test_empty_value(self):
        """Test that an empty value is allowed"""
        empty_value = ["", "   "]
        for value in empty_value:
            with pytest.raises(ValueError):
                SkuAttributeValue(
                    sku_id=self.test_sku1.id,
                    attribute_id=self.test_attribute2.id,
                    value=value
                )

    def test_update_to_empty_value(self):
        """Test that updating to an empty value is allowed"""
        empty_value = ["", "   "]
        for value in empty_value:
            sku_attribute_value = SkuAttributeValue(
                sku_id=self.test_sku1.id,
                attribute_id=self.test_attribute2.id,
                value="Test Value"
            )
            with pytest.raises(ValueError):
                sku_attribute_value.value = value


class TestSkuAttributeValueSkuRelationship:
    """Test suite for SkuAttributeValue model relationships with Sku model"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_sku_attribute_values):
        """Setup method for the test suite"""
        (
            self.test_sku1, self.test_sku2, self.test_attribute1,
            self.test_attribute2, self.test_sku_attr_value1, self.test_sku_attr_value2
        ) = setup_sku_attribute_values

    @pytest.mark.asyncio
    async def test_sku_attribute_value_with_sku_relationship(
        self, db_session: AsyncSession
    ):
        """Test that a sku attribute value with a sku relationship properly loads"""
        retrieved_sku_attribute_value = await get_object_by_id(
            db_session,
            SkuAttributeValue,
            self.test_sku_attr_value1.id
        )

        assert retrieved_sku_attribute_value.sku_id == self.test_sku1.id
        assert retrieved_sku_attribute_value.sku == self.test_sku1
        assert retrieved_sku_attribute_value.sku.name == "Test Sku 1"

    @pytest.mark.asyncio
    async def test_sku_attribute_value_without_sku_relationship(
        self, db_session: AsyncSession
    ):
        """Test sku attribute value without sku relationship"""
        item = SkuAttributeValue(
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_sku_attribute_value_to_different_sku(
        self, db_session: AsyncSession, sku_factory
    ):
        """Test updating a sku attribute value to a different sku"""
        another_sku = await sku_factory(name="Another Sku")
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        await save_object(db_session, sku_attribute_value)

        assert sku_attribute_value.sku_id == self.test_sku1.id
        assert sku_attribute_value.sku == self.test_sku1
        assert sku_attribute_value.sku.name == "Test Sku 1"

        sku_attribute_value.sku_id = another_sku.id
        await save_object(db_session, sku_attribute_value)

        assert sku_attribute_value.sku_id == another_sku.id
        assert sku_attribute_value.sku == another_sku
        assert sku_attribute_value.sku.name == "Another Sku"

    @pytest.mark.asyncio
    async def test_create_sku_attribute_value_with_invalid_sku_id(
        self, db_session: AsyncSession
    ):
        """Test creating a sku attribute value with an invalid sku_id"""
        item = SkuAttributeValue(
            sku_id=999,
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_sku_attribute_value_with_invalid_sku_id(
        self, db_session: AsyncSession
    ):
        """Test updating a sku attribute value with an invalid sku_id"""
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        await save_object(db_session, sku_attribute_value)

        sku_attribute_value.sku_id = 999
        with pytest.raises(IntegrityError):
            await save_object(db_session, sku_attribute_value)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_setting_sku_id_to_null_fails(self, db_session: AsyncSession):
        """Test that setting a sku attribute value's sku_id to None fails"""
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        await save_object(db_session, sku_attribute_value)
        sku_attribute_value.sku_id = None
        with pytest.raises(IntegrityError):
            await save_object(db_session, sku_attribute_value)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_sku_attribute_value_with_sku_relationship(
        self, db_session: AsyncSession
    ):
        """Test deleting a sku attribute value with a sku relationship"""
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        await save_object(db_session, sku_attribute_value)

        sku = await get_object_by_id(
            db_session,
            Skus,
            self.test_sku1.id
        )
        await db_session.refresh(sku, ['sku_attribute_values'])

        assert sku.sku_attribute_values == [
            self.test_sku_attr_value1,
            sku_attribute_value
        ]

        await delete_object(db_session, sku_attribute_value)

        deleted_sku_attribute_value = await get_object_by_id(
            db_session,
            SkuAttributeValue,
            sku_attribute_value.id
        )
        assert deleted_sku_attribute_value is None

        await db_session.refresh(sku, ['sku_attribute_values'])
        assert sku is not None
        assert sku.name == "Test Sku 1"
        assert sku.sku_attribute_values == [self.test_sku_attr_value1]


class TestSkuAttributeValueAttributeRelationship:
    """Test suite for SkuAttributeValue model relationships with Attribute model"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_sku_attribute_values):
        """Setup method for the test suite"""
        (
            self.test_sku1, self.test_sku2, self.test_attribute1,
            self.test_attribute2, self.test_sku_attr_value1, self.test_sku_attr_value2
        ) = setup_sku_attribute_values

    @pytest.mark.asyncio
    async def test_sku_attribute_value_with_attribute_relationship(
        self, db_session: AsyncSession
    ):
        """
        Test that a sku attribute value with an attribute relationship properly
        loads.
        """
        retrieved_sku_attribute_value = await get_object_by_id(
            db_session,
            SkuAttributeValue,
            self.test_sku_attr_value1.id
        )

        assert retrieved_sku_attribute_value.attribute_id == self.test_attribute1.id
        assert retrieved_sku_attribute_value.attribute == self.test_attribute1
        assert retrieved_sku_attribute_value.attribute.name == "Test Attribute 1"

    @pytest.mark.asyncio
    async def test_sku_attribute_value_without_attribute_relationship(
        self, db_session: AsyncSession
    ):
        """
        Test that a sku attribute value without an attribute relationship fails to
        save.
        """
        item = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            value="Test Value"
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_sku_attribute_value_to_different_attribute(
        self, db_session: AsyncSession, attribute_factory
    ):
        """
        Test that updating a sku attribute value to a different attribute succeeds.
        """
        another_attribute = await attribute_factory(
            name="Another Attribute",
            data_type="TEXT"
        )
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        await save_object(db_session, sku_attribute_value)

        assert sku_attribute_value.attribute_id == self.test_attribute2.id
        assert sku_attribute_value.attribute == self.test_attribute2
        assert sku_attribute_value.attribute.name == "Test Attribute 2"

        sku_attribute_value.attribute_id = another_attribute.id
        await save_object(db_session, sku_attribute_value)

        assert sku_attribute_value.attribute_id == another_attribute.id
        assert sku_attribute_value.attribute == another_attribute
        assert sku_attribute_value.attribute.name == "Another Attribute"

    @pytest.mark.asyncio
    async def test_create_sku_attribute_value_with_invalid_attribute_id(
        self, db_session: AsyncSession
    ):
        """
        Test that creating a sku attribute value with an invalid attribute_id fails.
        """
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=999,
            value="Test Value"
        )

        with pytest.raises(IntegrityError):
            await save_object(db_session, sku_attribute_value)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_sku_attribute_value_with_invalid_attribute_id(
        self, db_session: AsyncSession
    ):
        """
        Test that updating a sku attribute value with an invalid attribute_id fails.
        """
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        await save_object(db_session, sku_attribute_value)

        sku_attribute_value.attribute_id = 999
        with pytest.raises(IntegrityError):
            await save_object(db_session, sku_attribute_value)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_setting_attribute_id_to_null_fails(self, db_session: AsyncSession):
        """
        Test that setting a sku attribute value's attribute_id to None fails.
        """
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        await save_object(db_session, sku_attribute_value)
        sku_attribute_value.attribute_id = None
        with pytest.raises(IntegrityError):
            await save_object(db_session, sku_attribute_value)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_sku_attribute_value_with_attribute_relationship(
        self, db_session: AsyncSession
    ):
        """
        Test that deleting a sku attribute value with an attribute relationship
        properly removes the relationship.
        """
        sku_attribute_value = SkuAttributeValue(
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute2.id,
            value="Test Value"
        )
        await save_object(db_session, sku_attribute_value)

        attribute = await get_object_by_id(
            db_session,
            Attributes,
            self.test_attribute2.id
        )
        await db_session.refresh(attribute, ['sku_attribute_values'])

        assert attribute.sku_attribute_values == [
            self.test_sku_attr_value2, sku_attribute_value
        ]

        await delete_object(db_session, sku_attribute_value)

        deleted_sku_attribute_value = await get_object_by_id(
            db_session,
            SkuAttributeValue,
            sku_attribute_value.id
        )
        assert deleted_sku_attribute_value is None

        await db_session.refresh(attribute, ['sku_attribute_values'])
        assert attribute is not None
        assert attribute.name == "Test Attribute 2"
        assert attribute.sku_attribute_values == [self.test_sku_attr_value2]
