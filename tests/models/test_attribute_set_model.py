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
    async def setup_objects(self, db_session: AsyncSession):
        """Setup method for the test suite"""
        self.test_attribute_set1 = AttributeSets(
            name="Electronics"
        )
        await save_object(db_session, self.test_attribute_set1)

        self.test_attribute_set2 = AttributeSets(
            name="Clothing"
        )
        await save_object(db_session, self.test_attribute_set2)

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
        assert self.test_attribute_set1.name == "Electronics"
        assert self.test_attribute_set1.slug == "electronics"
        assert self.test_attribute_set2.name == "Clothing"
        assert self.test_attribute_set2.slug == "clothing"

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test create operation"""
        new_set = AttributeSets(name="Home Goods")
        await save_object(db_session, new_set)
        assert new_set.id is not None
        assert new_set.name == "Home Goods"
        assert new_set.slug == "home-goods"
        assert await count_model_objects(db_session, AttributeSets) == 3

    @pytest.mark.asyncio
    async def test_slug_uniqueness(self, db_session: AsyncSession):
        """Test slug uniqueness"""
        with pytest.raises(IntegrityError):
            duplicate_set = AttributeSets(name="Electronics")
            await save_object(db_session, duplicate_set)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test get operation"""
        retrieved_set = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        assert retrieved_set.name == "Electronics"
        all_sets = await get_all_objects(db_session, AttributeSets)
        assert len(all_sets) == 2

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test update operation"""
        self.test_attribute_set1.name = "Digital Gadgets"
        await save_object(db_session, self.test_attribute_set1)
        updated_set = await get_object_by_id(
            db_session, AttributeSets, self.test_attribute_set1.id
        )
        assert updated_set.name == "Digital Gadgets"
        assert updated_set.slug == "digital-gadgets"

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
- pindahkan test_setting_parent_id_to_null_fails ke test children -> parent
- tambahkan test_update_parent_children di test parent -> children
- balik test_setting_attribute_to_empty_list menjadi test_setting_attribute_attribute_sets_to_empty_list
"""