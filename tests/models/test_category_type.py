from sqlalchemy import String, event
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from app.models.category_type import CategoryTypes
from app.core.listeners import _set_slug
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
)


class TestCategoryType:
    """Test suite for CategoryType model"""
    @pytest.fixture(autouse=True)
    async def setup_objects(self, db_session: AsyncSession):
        """Setup method for the test suite"""
        # Create category type
        self.test_category_type1 = CategoryTypes(
            name="test category type"
        )
        await save_object(db_session, self.test_category_type1)

        # Create category type with a different name
        self.test_category_type2 = CategoryTypes(
            name="test category type 2"
        )
        await save_object(db_session, self.test_category_type2)

    def test_inheritance_from_base_model(self):
        """Test that CategoryType model inherits from Base model"""
        assert issubclass(CategoryTypes, Base)

    def test_fields_with_validation(self):
        """Test that CategoryType model has fields with validation"""
        assert not hasattr(CategoryTypes, 'validate_name')
        assert len(CategoryTypes.__mapper__.validators) == 0

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(CategoryTypes.name, 'set', _set_slug)
        assert not event.contains(CategoryTypes, 'set', _set_slug)

    def test_name_field_properties(self):
        """Test the properties of the name field"""
        name_column = CategoryTypes.__table__.columns.get('name')
        assert name_column is not None
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 100
        assert name_column.nullable is False
        assert name_column.unique is True
        assert name_column.index is True
        assert name_column.default is None

    def test_slug_field_properties(self):
        """Test the properties of the slug field"""
        slug_column = CategoryTypes.__table__.columns.get('slug')
        assert slug_column is not None
        assert isinstance(slug_column.type, String)
        assert slug_column.type.length == 100
        assert slug_column.nullable is False
        assert slug_column.unique is True
        assert slug_column.index is True
        assert slug_column.default is None

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_category_type1)
        assert str_repr == (
            "CategoryTypes(name=test category type, slug=test-category-type)"
        )

    def test_init_method(self):
        """Test the init method"""
        assert self.test_category_type1.id == 1
        assert self.test_category_type1.name == "test category type"
        assert self.test_category_type1.slug == "test-category-type"

        assert self.test_category_type2.id == 2
        assert self.test_category_type2.name == "test category type 2"
        assert self.test_category_type2.slug == "test-category-type-2"

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = CategoryTypes(name="test category type 3")
        await save_object(db_session, item)

        assert item.id == 3
        assert item.name == "test category type 3"
        assert item.slug == "test-category-type-3"

        item_with_slug = CategoryTypes(
            name="test category type 4",
            slug="slug-category-type-4"
        )
        await save_object(db_session, item_with_slug)
        assert item_with_slug.id == 4
        assert item_with_slug.name == "test category type 4"
        # slug should be set to the slugified name
        assert item_with_slug.slug == "test-category-type-4"

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type1.id
        )
        assert item.id == 1
        assert item.name == "test category type"
        assert item.slug == "test-category-type"

        item = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type2.id
        )
        assert item.id == 2
        assert item.name == "test category type 2"
        assert item.slug == "test-category-type-2"

        items = await get_all_objects(db_session, CategoryTypes)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].name == "test category type"
        assert items[0].slug == "test-category-type"

        assert items[1].id == 2
        assert items[1].name == "test category type 2"
        assert items[1].slug == "test-category-type-2"

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type1.id
        )
        item.name = "updated test category type"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test category type"
        assert item.slug == "updated-test-category-type"

        item.slug = "updated-slug-category-type"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test category type"
        # slug keep the same
        assert item.slug == "updated-test-category-type"

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_category_type1)

        item = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type1.id
        )
        assert item is None

        items = await get_all_objects(db_session, CategoryTypes)
        assert len(items) == 1
