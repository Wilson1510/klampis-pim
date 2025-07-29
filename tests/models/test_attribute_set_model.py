import pytest
from sqlalchemy import String, event, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import Base
from app.models import (
    Attributes, AttributeSets, Categories
)
from app.core.listeners import _set_slug
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    count_model_objects,
    assert_relationship
)


@pytest.fixture
async def setup_attribute_sets(attribute_set_factory):
    """Fixture to create attribute sets for the test suite"""
    attribute_set1 = await attribute_set_factory(
        name="Test Attribute Set 1"
    )
    attribute_set2 = await attribute_set_factory(
        name="Test Attribute Set 2"
    )
    return attribute_set1, attribute_set2


class TestAttributeSet:
    """Test suite for AttributeSet model"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_attribute_sets):
        """Setup method for the test suite"""
        self.test_attribute_set1, self.test_attribute_set2 = setup_attribute_sets

    def test_inheritance_from_base_model(self):
        """Test that AttributeSet model inherits from Base model"""
        assert issubclass(AttributeSets, Base)

    def test_fields_with_validation(self):
        """Test that the fields have the expected validation"""
        assert not hasattr(AttributeSets, 'validate_name')
        assert len(AttributeSets.__mapper__.validators) == 0

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(AttributeSets.name, 'set', _set_slug)
        assert not event.contains(AttributeSets, 'set', _set_slug)

    def test_name_field_properties(self):
        """Test the properties of the name field"""
        name_column = AttributeSets.__table__.columns.get('name')
        assert name_column is not None
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 100
        assert name_column.nullable is False
        assert name_column.unique is None
        assert name_column.index is True
        assert name_column.default is None

    def test_slug_field_properties(self):
        """Test the properties of the slug field"""
        slug_column = AttributeSets.__table__.columns.get('slug')
        assert slug_column is not None
        assert isinstance(slug_column.type, String)
        assert slug_column.type.length == 100
        assert slug_column.unique is True
        assert slug_column.nullable is False
        assert slug_column.index is True
        assert slug_column.default is None

    def test_relationships(self):
        """Test relationships"""
        assert_relationship(AttributeSets, "attributes", "attribute_sets")
        assert_relationship(AttributeSets, "categories", "attribute_sets")

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_attribute_set1)
        assert str_repr == "AttributeSets(Test Attribute Set 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        await db_session.refresh(self.test_attribute_set1, ['attributes'])
        await db_session.refresh(self.test_attribute_set1, ['categories'])

        await db_session.refresh(self.test_attribute_set2, ['attributes'])
        await db_session.refresh(self.test_attribute_set2, ['categories'])

        assert self.test_attribute_set1.id == 1
        assert self.test_attribute_set1.name == "Test Attribute Set 1"
        assert self.test_attribute_set1.slug == "test-attribute-set-1"
        assert self.test_attribute_set1.attributes == []
        assert self.test_attribute_set1.categories == []

        assert self.test_attribute_set2.id == 2
        assert self.test_attribute_set2.name == "Test Attribute Set 2"
        assert self.test_attribute_set2.slug == "test-attribute-set-2"
        assert self.test_attribute_set2.attributes == []
        assert self.test_attribute_set2.categories == []

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test create operation"""
        item = AttributeSets(name="Test Attribute Set 3")
        await save_object(db_session, item)
        assert item.id is not None
        assert item.name == "Test Attribute Set 3"
        assert item.slug == "test-attribute-set-3"
        assert await count_model_objects(db_session, AttributeSets) == 3

        # Test default slug
        item_with_slug = AttributeSets(
            name="Test Attribute Set 4",
            slug="slug-attribute-set-4"
        )
        await save_object(db_session, item_with_slug)
        assert item_with_slug.id == 4
        assert item_with_slug.name == "Test Attribute Set 4"
        # slug should be set to the slugified name
        assert item_with_slug.slug == "test-attribute-set-4"
        assert await count_model_objects(db_session, AttributeSets) == 4

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test get operation"""
        item = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        assert item.id == 1
        assert item.name == "Test Attribute Set 1"
        assert item.slug == "test-attribute-set-1"

        item = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set2.id
        )
        assert item.name == "Test Attribute Set 2"
        assert item.slug == "test-attribute-set-2"

        items = await get_all_objects(db_session, AttributeSets)
        assert len(items) == 2
        assert items[0].name == "Test Attribute Set 1"
        assert items[0].slug == "test-attribute-set-1"
        assert items[1].name == "Test Attribute Set 2"
        assert items[1].slug == "test-attribute-set-2"

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test update operation"""
        item = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        item.name = "Test Attribute Set 1 Updated"
        await save_object(db_session, item)
        assert item.id == 1
        assert item.name == "Test Attribute Set 1 Updated"
        assert item.slug == "test-attribute-set-1-updated"
        assert await count_model_objects(db_session, AttributeSets) == 2

        item.slug = "updated-slug-attribute-set-1"
        await save_object(db_session, item)
        assert item.id == 1
        assert item.name == "Test Attribute Set 1 Updated"
        # slug should be the same
        assert item.slug == "test-attribute-set-1-updated"
        assert await count_model_objects(db_session, AttributeSets) == 2

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test delete operation"""
        await delete_object(db_session, self.test_attribute_set1)

        item = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        assert item is None
        assert await count_model_objects(db_session, AttributeSets) == 1


class TestAttributeSetCategoryRelationship:
    """Test suite for AttributeSet model relationships with Category model"""

    @pytest.fixture(autouse=True)
    async def setup_objects(self, setup_attribute_sets, category_type_factory):
        """Setup method for the test suite"""
        self.test_attribute_set1, self.test_attribute_set2 = setup_attribute_sets
        self.test_category_type = await category_type_factory()

    @pytest.mark.asyncio
    async def test_create_attribute_set_with_categories(self, db_session: AsyncSession):
        """Test creating an attribute set and associating it with multiple categories"""
        attribute_set = AttributeSets(
            name="Test Attribute Set with Categories",
            categories=[
                Categories(
                    name="Test Category 1",
                    category_type_id=self.test_category_type.id
                ),
                Categories(
                    name="Test Category 2",
                    category_type_id=self.test_category_type.id
                )
            ]
        )
        await save_object(db_session, attribute_set)

        retrieved_attribute_set = await get_object_by_id(
            db_session, AttributeSets, attribute_set.id
        )

        await db_session.refresh(retrieved_attribute_set, ['categories'])

        assert retrieved_attribute_set.id == 3
        assert retrieved_attribute_set.name == "Test Attribute Set with Categories"
        assert len(retrieved_attribute_set.categories) == 2
        assert retrieved_attribute_set.categories[0].name == "Test Category 1"
        assert retrieved_attribute_set.categories[1].name == "Test Category 2"

    @pytest.mark.asyncio
    async def test_add_multiple_categories_to_attribute_set(
        self, db_session: AsyncSession
    ):
        """Test adding multiple categories to an attribute set"""
        for i in range(5):
            category = Categories(
                name=f"Test Category {i}",
                description=f"Test Description {i}",
                category_type_id=self.test_category_type.id,
                attribute_sets=[self.test_attribute_set1]
            )
            await save_object(db_session, category)

        retrieved_attribute_set = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )

        await db_session.refresh(retrieved_attribute_set, ['categories'])

        assert len(retrieved_attribute_set.categories) == 5
        for i in range(5):
            assert retrieved_attribute_set.categories[i].id == i + 1
            assert retrieved_attribute_set.categories[i].name == (
                f"Test Category {i}"
            )
            assert retrieved_attribute_set.categories[i].description == (
                f"Test Description {i}"
            )

    @pytest.mark.asyncio
    async def test_update_attribute_sets_categories(self, db_session: AsyncSession):
        """Test updating an attribute set's categories"""
        attribute_set = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        await db_session.refresh(attribute_set, ['categories'])
        assert len(attribute_set.categories) == 0

        attribute_set.categories = [
            Categories(
                name="Test Category 1",
                category_type_id=self.test_category_type.id
            ),
            Categories(
                name="Test Category 2",
                category_type_id=self.test_category_type.id
            )
        ]
        await save_object(db_session, attribute_set)
        await db_session.refresh(attribute_set, ['categories'])

        assert len(attribute_set.categories) == 2
        assert attribute_set.categories[0].name == "Test Category 1"
        assert attribute_set.categories[1].name == "Test Category 2"

        attribute_set.categories = [
            Categories(
                name="Test Category 3",
                category_type_id=self.test_category_type.id
            )
        ]
        await save_object(db_session, attribute_set)
        await db_session.refresh(attribute_set, ['categories'])
        assert len(attribute_set.categories) == 1
        assert attribute_set.categories[0].name == "Test Category 3"

    @pytest.mark.asyncio
    async def test_attribute_set_deletion_with_categories(
        self, db_session: AsyncSession
    ):
        """Test deleting an attribute set with categories"""
        category = Categories(
            name="Test Category 1",
            category_type_id=self.test_category_type.id,
            attribute_sets=[self.test_attribute_set1]
        )
        await save_object(db_session, category)
        await db_session.refresh(category, ['attribute_sets'])
        assert len(category.attribute_sets) == 1
        assert category.attribute_sets[0].id == 1
        assert category.attribute_sets[0].name == "Test Attribute Set 1"

        await delete_object(db_session, self.test_attribute_set1)

        item = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        assert item is None
        assert await count_model_objects(db_session, AttributeSets) == 1

        item = await get_object_by_id(
            db_session, Categories, category.id
        )
        assert item is not None

    @pytest.mark.asyncio
    async def test_orphaned_category_cleanup(self, db_session: AsyncSession):
        """Test handling of categories when their attribute set is deleted"""
        temp_attribute_set = AttributeSets(
            name="Temporary Attribute Set for Category test"
        )
        await save_object(db_session, temp_attribute_set)

        temp_category = Categories(
            name="Temporary Category for Attribute Set test",
            category_type_id=self.test_category_type.id,
            attribute_sets=[temp_attribute_set]
        )
        await save_object(db_session, temp_category)

        await delete_object(db_session, temp_attribute_set)

        item = await get_object_by_id(
            db_session, AttributeSets, temp_attribute_set.id
        )
        assert item is None
        assert await count_model_objects(db_session, AttributeSets) == 2

        item = await get_object_by_id(
            db_session, Categories, temp_category.id
        )
        assert item is not None

    @pytest.mark.asyncio
    async def test_query_attribute_set_by_category(self, db_session: AsyncSession):
        """Test querying an attribute set by category"""
        category1 = Categories(
            name="Test Category 1",
            category_type_id=self.test_category_type.id,
            attribute_sets=[self.test_attribute_set1]
        )
        await save_object(db_session, category1)

        category2 = Categories(
            name="Test Category 2",
            category_type_id=self.test_category_type.id,
            attribute_sets=[self.test_attribute_set1]
        )
        await save_object(db_session, category2)

        stmt = select(AttributeSets).join(AttributeSets.categories).where(
            Categories.name == "Test Category 1"
        )
        result = await db_session.execute(stmt)
        attribute_sets = result.scalars().all()
        assert len(attribute_sets) == 1
        assert self.test_attribute_set1 in attribute_sets


class TestAttributeSetAttributeRelationship:
    """Test suite for AttributeSet model relationships with Attribute model"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_attribute_sets):
        """Setup method for the test suite"""
        self.test_attribute_set1, self.test_attribute_set2 = setup_attribute_sets

    @pytest.mark.asyncio
    async def test_create_attribute_set_with_attributes(self, db_session: AsyncSession):
        """Test creating an attribute set and associating it with multiple attributes"""
        attribute_set = AttributeSets(
            name="Test Attribute Set with Attributes",
            attributes=[
                Attributes(name="Test Attribute 1"),
                Attributes(name="Test Attribute 2")
            ]
        )
        await save_object(db_session, attribute_set)

        retrieved_attribute_set = await get_object_by_id(
            db_session, AttributeSets, attribute_set.id
        )
        await db_session.refresh(retrieved_attribute_set, ['attributes'])

        assert retrieved_attribute_set.id == 3
        assert retrieved_attribute_set.name == "Test Attribute Set with Attributes"
        assert len(retrieved_attribute_set.attributes) == 2
        assert retrieved_attribute_set.attributes[0].name == "Test Attribute 1"
        assert retrieved_attribute_set.attributes[1].name == "Test Attribute 2"

    @pytest.mark.asyncio
    async def test_add_multiple_attributes_to_attribute_set(
        self, db_session: AsyncSession
    ):
        """Test adding multiple attributes to an attribute set"""
        for i in range(5):
            attribute = Attributes(
                name=f"Test Attribute {i}",
                attribute_sets=[self.test_attribute_set1]
            )
            await save_object(db_session, attribute)

        retrieved_attribute_set = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        await db_session.refresh(retrieved_attribute_set, ['attributes'])

        assert len(retrieved_attribute_set.attributes) == 5
        for i in range(5):
            assert retrieved_attribute_set.attributes[i].id == i + 1
            assert retrieved_attribute_set.attributes[i].name == (
                f"Test Attribute {i}"
            )

    @pytest.mark.asyncio
    async def test_update_attributes_attribute_sets(self, db_session: AsyncSession):
        """Test updating an attribute set's attributes"""
        attribute_set = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        await db_session.refresh(attribute_set, ['attributes'])
        assert len(attribute_set.attributes) == 0

        attribute_set.attributes = [
            Attributes(name="Test Attribute 1"),
            Attributes(name="Test Attribute 2")
        ]
        await save_object(db_session, attribute_set)
        await db_session.refresh(attribute_set, ['attributes'])

        assert len(attribute_set.attributes) == 2
        assert attribute_set.attributes[0].name == "Test Attribute 1"
        assert attribute_set.attributes[1].name == "Test Attribute 2"

        attribute_set.attributes = [
            Attributes(name="Test Attribute 3"),
            Attributes(name="Test Attribute 4"),
            Attributes(name="Test Attribute 5")
        ]
        await save_object(db_session, attribute_set)
        await db_session.refresh(attribute_set, ['attributes'])
        assert len(attribute_set.attributes) == 3
        assert attribute_set.attributes[0].name == "Test Attribute 3"
        assert attribute_set.attributes[1].name == "Test Attribute 4"
        assert attribute_set.attributes[2].name == "Test Attribute 5"

    @pytest.mark.asyncio
    async def test_attribute_set_deletion_with_attributes(
        self, db_session: AsyncSession
    ):
        """Test deleting an attribute set with attributes"""
        attribute = Attributes(
            name="Test Attribute 1",
            attribute_sets=[
                self.test_attribute_set1,
                self.test_attribute_set2
            ]
        )
        await save_object(db_session, attribute)
        await db_session.refresh(attribute, ['attribute_sets'])
        assert len(attribute.attribute_sets) == 2

        await delete_object(db_session, self.test_attribute_set1)
        await delete_object(db_session, self.test_attribute_set2)
        await db_session.refresh(attribute, ['attribute_sets'])
        assert len(attribute.attribute_sets) == 0

        test_attribute_set1 = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        test_attribute_set2 = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set2.id
        )
        assert test_attribute_set1 is None
        assert test_attribute_set2 is None

    @pytest.mark.asyncio
    async def test_setting_attribute_set_attributes_to_empty_list(
        self, db_session: AsyncSession
    ):
        """Test setting an attribute set's attributes to an empty list"""
        attribute = Attributes(
            name="Test Attribute 1",
            attribute_sets=[
                self.test_attribute_set1,
                self.test_attribute_set2
            ]
        )
        await save_object(db_session, attribute)
        await db_session.refresh(attribute, ['attribute_sets'])
        assert len(attribute.attribute_sets) == 2

        attribute.attribute_sets = []
        await save_object(db_session, attribute)
        await db_session.refresh(attribute, ['attribute_sets'])
        assert len(attribute.attribute_sets) == 0

        test_attribute_set1 = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        test_attribute_set2 = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set2.id
        )
        assert test_attribute_set1 is not None
        assert test_attribute_set2 is not None

    @pytest.mark.asyncio
    async def test_query_attribute_set_by_attribute(self, db_session: AsyncSession):
        """Test querying an attribute set by attribute"""
        attribute1 = Attributes(
            name="Test Attribute 1",
            attribute_sets=[
                self.test_attribute_set1,
                self.test_attribute_set2
            ]
        )
        await save_object(db_session, attribute1)

        attribute2 = Attributes(
            name="Test Attribute 2",
            attribute_sets=[
                self.test_attribute_set1,
                self.test_attribute_set2
            ]
        )
        await save_object(db_session, attribute2)

        stmt = select(AttributeSets).join(AttributeSets.attributes).where(
            Attributes.name == "Test Attribute 1"
        )
        result = await db_session.execute(stmt)
        attribute_sets = result.scalars().all()
        assert len(attribute_sets) == 2
        assert self.test_attribute_set1 in attribute_sets
        assert self.test_attribute_set2 in attribute_sets
