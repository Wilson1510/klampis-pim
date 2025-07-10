import pytest
from sqlalchemy import String, event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.base import Base
from app.models.attribute_set_model import AttributeSets
from app.core.listeners import _set_slug
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    count_model_objects,
    assert_relationship
)


class TestAttributeSet:
    """Test suite for AttributeSet model"""

    @pytest.fixture(autouse=True)
    async def setup_objects(self, db_session: AsyncSession, attribute_set_factory):
        """Setup method for the test suite"""
        self.test_attribute_set1 = await attribute_set_factory(
            name="Test Attribute Set 1"
        )
        self.test_attribute_set2 = await attribute_set_factory(
            name="Test Attribute Set 2"
        )

    def test_inheritance_from_base_model(self):
        """Test that AttributeSet model inherits from Base model"""
        assert issubclass(AttributeSets, Base)

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(AttributeSets.name, 'set', _set_slug)

    def test_name_field_properties(self):
        """Test the properties of the name field"""
        name_column = AttributeSets.__table__.columns.get('name')
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 100
        assert name_column.nullable is False

    def test_slug_field_properties(self):
        """Test the properties of the slug field"""
        slug_column = AttributeSets.__table__.columns.get('slug')
        assert isinstance(slug_column.type, String)
        assert slug_column.type.length == 100
        assert slug_column.unique is True

    def test_relationships(self):
        """Test relationships"""
        assert_relationship(AttributeSets, "attributes", "attribute_sets")

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        assert self.test_attribute_set1.name == "Test Attribute Set 1"
        assert self.test_attribute_set1.slug == "test-attribute-set-1"
        assert self.test_attribute_set2.name == "Test Attribute Set 2"
        assert self.test_attribute_set2.slug == "test-attribute-set-2"

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test create operation"""
        new_set = AttributeSets(name="Test Attribute Set 3")
        await save_object(db_session, new_set)
        assert new_set.id is not None
        assert new_set.name == "Test Attribute Set 3"
        assert new_set.slug == "test-attribute-set-3"
        assert await count_model_objects(db_session, AttributeSets) == 3

    @pytest.mark.asyncio
    async def test_slug_uniqueness(self, db_session: AsyncSession):
        """Test slug uniqueness"""
        with pytest.raises(IntegrityError):
            duplicate_set = AttributeSets(name="Test Attribute Set 1")
            await save_object(db_session, duplicate_set)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test get operation"""
        retrieved_set = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        assert retrieved_set.name == "Test Attribute Set 1"
        all_sets = await get_all_objects(db_session, AttributeSets)
        assert len(all_sets) == 2

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test update operation"""
        self.test_attribute_set1.name = "Test Attribute Set 1 Updated"
        await save_object(db_session, self.test_attribute_set1)
        updated_set = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        assert updated_set.name == "Test Attribute Set 1 Updated"
        assert updated_set.slug == "test-attribute-set-1-updated"

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test delete operation"""
        await delete_object(db_session, self.test_attribute_set1)
        assert await count_model_objects(db_session, AttributeSets) == 1
        deleted_set = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        assert deleted_set is None

"""
belum selesai
"""