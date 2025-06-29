from sqlalchemy import String, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from app.models.category_type_model import CategoryTypes
from app.models.category_model import Categories
from app.core.listeners import _set_slug
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
)


class TestCategoryType:
    """Test suite for CategoryType model and relationships"""
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
        assert name_column.unique is None
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

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""

        # refresh the test category type 1 and 2 to get the categories
        await db_session.refresh(self.test_category_type1, ['categories'])
        await db_session.refresh(self.test_category_type2, ['categories'])

        assert self.test_category_type1.id == 1
        assert self.test_category_type1.name == "test category type"
        assert self.test_category_type1.slug == "test-category-type"
        assert self.test_category_type1.categories == []

        assert self.test_category_type2.id == 2
        assert self.test_category_type2.name == "test category type 2"
        assert self.test_category_type2.slug == "test-category-type-2"
        assert self.test_category_type2.categories == []

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

    # Relationship Tests

    @pytest.mark.asyncio
    async def test_create_category_with_category_type(
        self, db_session: AsyncSession
    ):
        """Test creating top-level category with category type (valid scenario)"""
        # Top-level category must have category_type_id
        category = Categories(
            name="Test Category",
            description="Test Description",
            category_type_id=self.test_category_type1.id
        )
        await save_object(db_session, category)

        retrieved_category_type = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type1.id
        )
        await db_session.refresh(retrieved_category_type, ['categories'])

        assert len(retrieved_category_type.categories) == 1
        assert retrieved_category_type.categories[0].id == 1
        assert retrieved_category_type.categories[0].name == "Test Category"
        assert retrieved_category_type.categories[0].slug == "test-category"
        assert retrieved_category_type.categories[0].description == (
            "Test Description"
        )

    @pytest.mark.asyncio
    async def test_add_multiple_categories_to_category_type(
        self, db_session: AsyncSession
    ):
        """Test adding multiple categories to category type"""
        categories = []
        for i in range(5):
            category = Categories(
                name=f"Test Category {i}",
                description=f"Test Description {i}",
                category_type_id=self.test_category_type1.id
            )
            await save_object(db_session, category)
            categories.append(category)

        retrieved_category_type = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type1.id
        )
        await db_session.refresh(retrieved_category_type, ['categories'])

        assert len(retrieved_category_type.categories) == 5
        for i in range(5):
            assert retrieved_category_type.categories[i].id == i + 1
            assert retrieved_category_type.categories[i].name == f"Test Category {i}"
            assert retrieved_category_type.categories[i].slug == f"test-category-{i}"
            assert retrieved_category_type.categories[i].description == (
                f"Test Description {i}"
            )

    @pytest.mark.asyncio
    async def test_category_type_deletion_with_categories(
        self, db_session: AsyncSession
    ):
        """Test what happens when trying to delete category type with associated
        categories"""

        # Create categories associated with the type
        category = Categories(
            name="Test Category",
            category_type_id=self.test_category_type1.id
        )
        await save_object(db_session, category)

        # Try to delete category type that has associated categories
        with pytest.raises(IntegrityError):
            await delete_object(db_session, self.test_category_type1)

    @pytest.mark.asyncio
    async def test_reassigning_category_to_different_type(
        self, db_session: AsyncSession
    ):
        """Test reassigning category to different category type"""
        # Create category with test_category_type1
        category = Categories(
            name="Test Category",
            category_type_id=self.test_category_type1.id
        )
        await save_object(db_session, category)

        await db_session.refresh(category, ['category_type'])
        assert category.category_type.name == "test category type"

        # Reassign to test_category_type2
        category.category_type_id = self.test_category_type2.id
        await save_object(db_session, category)

        # Refresh and verify
        await db_session.refresh(category, ['category_type'])
        assert category.category_type.name == "test category type 2"

    @pytest.mark.asyncio
    async def test_setting_category_type_to_null_on_top_level_fails(
        self, db_session: AsyncSession
    ):
        """Test that setting category_type_id to NULL on top-level category fails"""

        # Create valid top-level category
        category = Categories(
            name="Test Category",
            category_type_id=self.test_category_type1.id
        )
        await save_object(db_session, category)

        # Try to set category_type_id to NULL (should fail constraint)
        category.category_type_id = None

        with pytest.raises(IntegrityError) as exc_info:
            await save_object(db_session, category)

        assert "chk_category_hierarchy_rule" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_orphaned_category_cleanup(self, db_session: AsyncSession):
        """Test handling of categories when their category type is deleted"""

        # Create temporary category type
        temp_type = CategoryTypes(name="Temporary Type")
        await save_object(db_session, temp_type)

        # Create category associated with temp type
        temp_category = Categories(
            name="Temporary Category",
            category_type_id=temp_type.id
        )
        await save_object(db_session, temp_category)

        # Try to delete the category type (should fail due to foreign key)
        with pytest.raises(IntegrityError):
            await delete_object(db_session, temp_type)
        await db_session.rollback()

        # To properly delete, first remove the category
        await delete_object(db_session, temp_category)

        # Now category type can be deleted
        await delete_object(db_session, temp_type)

        # Verify both are deleted
        deleted_category = await get_object_by_id(
            db_session, Categories, temp_category.id
        )
        deleted_type = await get_object_by_id(
            db_session, CategoryTypes, temp_type.id
        )

        assert deleted_category is None
        assert deleted_type is None

    @pytest.mark.asyncio
    async def test_query_category_type_by_categories(
        self, db_session: AsyncSession
    ):
        """Test querying category type by categories"""

        # Create categories associated with the type
        category = Categories(
            name="Test Category",
            category_type_id=self.test_category_type1.id
        )
        await save_object(db_session, category)

        category2 = Categories(
            name="Test Category 2",
            category_type_id=self.test_category_type2.id
        )
        await save_object(db_session, category2)

        # Query category type by categories
        stmt = select(CategoryTypes).join(Categories).where(
            Categories.name == "Test Category"
        )
        result = await db_session.execute(stmt)
        category_type = result.scalar_one_or_none()

        assert category_type.id == self.test_category_type1.id
        assert category_type.name == "test category type"
        assert category_type.slug == "test-category-type"
