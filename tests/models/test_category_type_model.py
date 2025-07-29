from sqlalchemy import String, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from app.models import CategoryTypes, Categories
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
async def setup_category_types(category_type_factory):
    """
    Fixture to create category types ONCE for the entire test module.
    This is the efficient part.
    """
    category_type1 = await category_type_factory(name="Test Category Type 1")
    category_type2 = await category_type_factory(name="Test Category Type 2")
    # Mengembalikan objek-objek yang sudah dibuat
    return category_type1, category_type2


class TestCategoryType:
    """Test suite for CategoryType model and relationships"""
    @pytest.fixture(autouse=True)
    def setup_class_data(self, setup_category_types):
        """
        Gets data from the module fixture and injects it into self.
        This runs once per class.
        """
        # Memasukkan hasil dari fixture modul ke dalam 'self'
        self.test_category_type1, self.test_category_type2 = setup_category_types

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

    def test_relationships_with_other_models(self):
        """Test the relationships with other models"""
        assert_relationship(CategoryTypes, "categories", "category_type")

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_category_type1)
        assert str_repr == "CategoryTypes(Test Category Type 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""

        # refresh the test category type 1 and 2 to get the categories
        await db_session.refresh(self.test_category_type1, ['categories'])
        await db_session.refresh(self.test_category_type2, ['categories'])

        assert self.test_category_type1.id == 1
        assert self.test_category_type1.name == "Test Category Type 1"
        assert self.test_category_type1.slug == "test-category-type-1"
        assert self.test_category_type1.categories == []

        assert self.test_category_type2.id == 2
        assert self.test_category_type2.name == "Test Category Type 2"
        assert self.test_category_type2.slug == "test-category-type-2"
        assert self.test_category_type2.categories == []

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = CategoryTypes(name="Test Category Type 3")
        await save_object(db_session, item)

        assert item.id == 3
        assert item.name == "Test Category Type 3"
        assert item.slug == "test-category-type-3"
        assert await count_model_objects(db_session, CategoryTypes) == 3

        item_with_slug = CategoryTypes(
            name="Test Category Type 4",
            slug="slug-category-type-4"
        )
        await save_object(db_session, item_with_slug)
        assert item_with_slug.id == 4
        assert item_with_slug.name == "Test Category Type 4"
        # slug should be set to the slugified name
        assert item_with_slug.slug == "test-category-type-4"
        assert await count_model_objects(db_session, CategoryTypes) == 4

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type1.id
        )
        assert item.id == 1
        assert item.name == "Test Category Type 1"
        assert item.slug == "test-category-type-1"

        item = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type2.id
        )
        assert item.id == 2
        assert item.name == "Test Category Type 2"
        assert item.slug == "test-category-type-2"

        items = await get_all_objects(db_session, CategoryTypes)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].name == "Test Category Type 1"
        assert items[0].slug == "test-category-type-1"

        assert items[1].id == 2
        assert items[1].name == "Test Category Type 2"
        assert items[1].slug == "test-category-type-2"

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type1.id
        )
        item.name = "updated test category type 1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test category type 1"
        assert item.slug == "updated-test-category-type-1"
        assert await count_model_objects(db_session, CategoryTypes) == 2

        item.slug = "updated-slug-category-type"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test category type 1"
        # slug keep the same
        assert item.slug == "updated-test-category-type-1"
        assert await count_model_objects(db_session, CategoryTypes) == 2

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
        assert await count_model_objects(db_session, CategoryTypes) == 1


class TestCategoryTypeCategoryRelationship:
    """
    Test suite for CategoryType model relationships with Categories model.
    """

    @pytest.fixture(autouse=True)
    def setup_class_data(self, setup_category_types):
        """
        Gets data from the module fixture and injects it into self.
        This runs once per class.
        """
        # Memasukkan hasil dari fixture modul ke dalam 'self'
        self.test_category_type1, self.test_category_type2 = setup_category_types

    @pytest.mark.asyncio
    async def test_create_category_type_with_categories(self, db_session: AsyncSession):
        """Test creating top-level category with category type (valid scenario)"""
        # Top-level category must have category_type_id
        category_type = CategoryTypes(
            name="Test Category Type 3",
            categories=[
                Categories(
                    name="Test Category 1",
                    description="Test Description 1"
                ),
                Categories(
                    name="Test Category 2",
                    description="Test Description 2"
                )
            ]
        )
        await save_object(db_session, category_type)

        retrieved_category_type = await get_object_by_id(
            db_session,
            CategoryTypes,
            category_type.id
        )
        await db_session.refresh(retrieved_category_type, ['categories'])

        assert retrieved_category_type.id == 3
        assert retrieved_category_type.name == "Test Category Type 3"
        assert retrieved_category_type.slug == "test-category-type-3"
        assert len(retrieved_category_type.categories) == 2

        assert retrieved_category_type.categories[0].id == 1
        assert retrieved_category_type.categories[0].name == "Test Category 1"
        assert retrieved_category_type.categories[0].slug == "test-category-1"
        assert retrieved_category_type.categories[0].description == "Test Description 1"

        assert retrieved_category_type.categories[1].id == 2
        assert retrieved_category_type.categories[1].name == "Test Category 2"
        assert retrieved_category_type.categories[1].slug == "test-category-2"
        assert retrieved_category_type.categories[1].description == "Test Description 2"

    @pytest.mark.asyncio
    async def test_add_multiple_categories_to_category_type(
        self, db_session: AsyncSession
    ):
        """Test adding multiple categories to category type"""
        for i in range(5):
            category = Categories(
                name=f"Test Category {i}",
                description=f"Test Description {i}",
                category_type_id=self.test_category_type1.id
            )
            await save_object(db_session, category)

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
    async def test_update_category_types_categories(self, db_session: AsyncSession):
        """Test updating the category type's categories"""
        category_type = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type1.id
        )
        await db_session.refresh(category_type, ['categories'])
        assert len(category_type.categories) == 0

        category_type.categories = [
            Categories(name="Test Category 1"),
            Categories(name="Test Category 2")
        ]
        await save_object(db_session, category_type)
        await db_session.refresh(category_type, ['categories'])
        assert len(category_type.categories) == 2
        assert category_type.categories[0].name == "Test Category 1"
        assert category_type.categories[1].name == "Test Category 2"

        category_type.categories = [
            Categories(name="Test Category 3"),
            Categories(name="Test Category 4"),
            Categories(name="Test Category 5")
        ]

        # should fail because Test Category 1 and Test Category 2 will lose their
        # category_type_id
        with pytest.raises(IntegrityError):
            await save_object(db_session, category_type)
        await db_session.rollback()

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
        await db_session.rollback()

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
    async def test_query_category_type_by_categories(self, db_session: AsyncSession):
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
        assert category_type.name == "Test Category Type 1"
        assert category_type.slug == "test-category-type-1"
