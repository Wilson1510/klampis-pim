from sqlalchemy import String, event, Text, Integer, CheckConstraint, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from app.models.category_type_model import CategoryTypes
from app.models.category_model import Categories
from app.models.product_model import Products
from app.models.supplier_model import Suppliers
from app.core.listeners import _set_slug
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    assert_relationship,
    count_model_objects
)


class TestCategory:
    """Test suite for Category model and relationships"""
    @pytest.fixture(autouse=True)
    async def setup_objects(self, db_session: AsyncSession):
        """Setup method for the test suite"""
        # Create category type
        self.test_category_type = CategoryTypes(
            name="test category type"
        )
        await save_object(db_session, self.test_category_type)

        # Create category
        self.test_category1 = Categories(
            name="test category 1",
            description="test category 1 description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, self.test_category1)

        self.test_category2 = Categories(
            name="test category 2",
            description="test category 2 description",
            parent_id=self.test_category1.id
        )
        await save_object(db_session, self.test_category2)

    def test_inheritance_from_base_model(self):
        """Test that Category model inherits from Base model"""
        assert issubclass(Categories, Base)

    def test_fields_with_validation(self):
        """Test that Category model has fields with validation"""
        assert not hasattr(Categories, 'validate_name')
        assert len(Categories.__mapper__.validators) == 0

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(Categories.name, 'set', _set_slug)
        assert not event.contains(Categories, 'set', _set_slug)

    def test_table_args(self):
        """Test that the table has the expected table args"""
        table_args = Categories.__table_args__

        # Check that we have exactly 2 constraints
        assert len(table_args) == 2

        # Check that both are CheckConstraints
        assert all(isinstance(arg, CheckConstraint) for arg in table_args)

        # Check constraint names and order
        constraint_names = [arg.name for arg in table_args]
        expected_names = [
            'check_category_hierarchy_rule',
            'check_category_no_self_reference'
        ]
        assert constraint_names == expected_names

        # Check constraint SQL text
        hierarchy_constraint = table_args[0]
        self_ref_constraint = table_args[1]

        assert str(hierarchy_constraint.sqltext) == (
            '(parent_id IS NULL AND category_type_id IS NOT NULL) OR '
            '(parent_id IS NOT NULL AND category_type_id IS NULL)'
        )
        assert str(self_ref_constraint.sqltext) == 'id <> parent_id'

    def test_name_field_properties(self):
        """Test the properties of the name field"""
        name_column = Categories.__table__.columns.get('name')
        assert name_column is not None
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 100
        assert name_column.nullable is False
        assert name_column.unique is None
        assert name_column.index is True
        assert name_column.default is None

    def test_slug_field_properties(self):
        """Test the properties of the slug field"""
        slug_column = Categories.__table__.columns.get('slug')
        assert slug_column is not None
        assert isinstance(slug_column.type, String)
        assert slug_column.type.length == 100
        assert slug_column.nullable is False
        assert slug_column.unique is True
        assert slug_column.index is True
        assert slug_column.default is None

    def test_description_field_properties(self):
        """Test the properties of the description field"""
        description_column = Categories.__table__.columns.get('description')
        assert description_column is not None
        assert isinstance(description_column.type, Text)
        assert description_column.nullable is True
        assert description_column.unique is None
        assert description_column.index is None
        assert description_column.default is None

    def test_category_type_id_field_properties(self):
        """Test the properties of the category_type_id field"""
        category_type_column = Categories.__table__.columns.get('category_type_id')
        assert category_type_column is not None
        assert isinstance(category_type_column.type, Integer)
        assert category_type_column.nullable is True
        foreign_key = list(category_type_column.foreign_keys)[0]
        assert str(foreign_key.target_fullname) == "category_types.id"
        assert category_type_column.unique is None
        assert category_type_column.index is True
        assert category_type_column.default is None

    def test_parent_id_field_properties(self):
        """Test the properties of the parent_id field"""
        parent_column = Categories.__table__.columns.get('parent_id')
        assert parent_column is not None
        assert isinstance(parent_column.type, Integer)
        assert parent_column.nullable is True
        foreign_key = list(parent_column.foreign_keys)[0]
        assert str(foreign_key.target_fullname) == "categories.id"
        assert parent_column.unique is None
        assert parent_column.index is True
        assert parent_column.default is None

    def test_relationships_with_other_models(self):
        """Test the relationships with other models"""
        assert_relationship(Categories, "category_type", "categories")
        assert_relationship(Categories, "parent", "children")
        assert_relationship(Categories, "children", "parent")
        assert_relationship(Categories, "products", "category")

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_category1)
        assert str_repr == "Categories(test category 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        await db_session.refresh(self.test_category1, ['children'])
        await db_session.refresh(self.test_category2, ['children'])

        await db_session.refresh(self.test_category1, ['products'])
        await db_session.refresh(self.test_category2, ['products'])

        assert self.test_category1.id == 1
        assert self.test_category1.name == "test category 1"
        assert self.test_category1.slug == "test-category-1"
        assert self.test_category1.description == "test category 1 description"
        assert self.test_category1.category_type_id == 1
        assert self.test_category1.category_type == self.test_category_type
        assert self.test_category1.parent_id is None
        assert self.test_category1.parent is None
        assert self.test_category1.children == [self.test_category2]
        assert self.test_category1.products == []

        assert self.test_category2.id == 2
        assert self.test_category2.name == "test category 2"
        assert self.test_category2.slug == "test-category-2"
        assert self.test_category2.description == "test category 2 description"
        assert self.test_category2.category_type_id is None
        assert self.test_category2.category_type is None
        assert self.test_category2.parent_id == self.test_category1.id
        assert self.test_category2.parent == self.test_category1
        assert self.test_category2.children == []
        assert self.test_category2.products == []

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = Categories(
            name="test category 3",
            description="test category 3 description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, item)

        assert item.id == 3
        assert item.name == "test category 3"
        assert item.slug == "test-category-3"
        assert item.description == "test category 3 description"
        assert item.category_type_id == 1
        assert item.parent_id is None
        assert await count_model_objects(db_session, Categories) == 3

        item_with_slug = Categories(
            name="test category 4",
            slug="slug-category-4",
            description="test category 4 description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, item_with_slug)
        assert item_with_slug.id == 4
        assert item_with_slug.name == "test category 4"
        # slug should be set to the slugified name
        assert item_with_slug.slug == "test-category-4"
        assert item_with_slug.description == "test category 4 description"
        assert item_with_slug.category_type_id == 1
        assert item_with_slug.parent_id is None
        assert await count_model_objects(db_session, Categories) == 4

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(db_session, Categories, self.test_category1.id)
        assert item.id == 1
        assert item.name == "test category 1"
        assert item.slug == "test-category-1"
        assert item.description == "test category 1 description"
        assert item.category_type_id == 1
        assert item.parent_id is None

        item = await get_object_by_id(db_session, Categories, self.test_category2.id)
        assert item.id == 2
        assert item.name == "test category 2"
        assert item.slug == "test-category-2"
        assert item.description == "test category 2 description"
        assert item.category_type_id is None
        assert item.parent_id == 1

        items = await get_all_objects(db_session, Categories)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].name == "test category 1"
        assert items[0].slug == "test-category-1"
        assert items[0].description == "test category 1 description"
        assert items[0].category_type_id == 1
        assert items[0].parent_id is None

        assert items[1].id == 2
        assert items[1].name == "test category 2"
        assert items[1].slug == "test-category-2"
        assert items[1].description == "test category 2 description"
        assert items[1].category_type_id is None
        assert items[1].parent_id == 1

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(db_session, Categories, self.test_category1.id)
        item.name = "updated test category 1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test category 1"
        assert item.slug == "updated-test-category-1"
        assert item.description == "test category 1 description"
        assert item.category_type_id == 1
        assert item.parent_id is None
        assert await count_model_objects(db_session, Categories) == 2

        item.slug = "updated-slug-category-1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test category 1"
        # slug keep the same
        assert item.slug == "updated-test-category-1"
        assert item.description == "test category 1 description"
        assert item.category_type_id == 1
        assert item.parent_id is None
        assert await count_model_objects(db_session, Categories) == 2

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_category2)

        item = await get_object_by_id(db_session, Categories, self.test_category2.id)
        assert item is None
        assert await count_model_objects(db_session, Categories) == 1

    """
    ================================================
    Database Constraint Tests (__table_args__)
    ================================================
    """

    @pytest.mark.asyncio
    async def test_valid_top_level_category_constraint(
        self, db_session: AsyncSession
    ):
        """Test valid top-level category: parent_id=NULL, category_type_id=NOT NULL"""
        category = Categories(
            name="valid top level category",
            description="test description",
            parent_id=None,
            category_type_id=self.test_category_type.id
        )

        # Should succeed - no exception raised
        await save_object(db_session, category)
        assert category.id is not None
        assert category.parent_id is None
        assert category.category_type_id == self.test_category_type.id

    @pytest.mark.asyncio
    async def test_valid_child_category_constraint(self, db_session: AsyncSession):
        """Test valid child category: parent_id=NOT NULL, category_type_id=NULL"""
        category = Categories(
            name="valid child category",
            description="test description",
            parent_id=self.test_category1.id,
            category_type_id=None
        )

        # Should succeed - no exception raised
        await save_object(db_session, category)
        assert category.id is not None
        assert category.parent_id == self.test_category1.id
        assert category.category_type_id is None

    @pytest.mark.asyncio
    async def test_invalid_both_null_constraint(self, db_session: AsyncSession):
        """Test invalid category: parent_id=NULL, category_type_id=NULL"""
        category = Categories(
            name="invalid both null category",
            description="test description",
            parent_id=None,
            category_type_id=None
        )

        # Should fail with IntegrityError due to constraint violation
        with pytest.raises(IntegrityError):
            await save_object(db_session, category)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_invalid_both_not_null_constraint(self, db_session: AsyncSession):
        """Test invalid category: parent_id=NOT NULL, category_type_id=NOT NULL"""
        category = Categories(
            name="invalid both not null category",
            description="test description",
            parent_id=self.test_category1.id,
            category_type_id=self.test_category_type.id
        )

        # Should fail with IntegrityError due to constraint violation
        with pytest.raises(IntegrityError):
            await save_object(db_session, category)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_violate_constraint_top_level_to_invalid(
        self, db_session: AsyncSession
    ):
        """Test updating top-level category to violate constraint"""
        # Create valid top-level category
        category = Categories(
            name="test update violation",
            description="test description",
            parent_id=None,
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, category)

        # Try to update to invalid state (both NULL)
        category.category_type_id = None
        # parent_id remains None

        with pytest.raises(IntegrityError):
            await save_object(db_session, category)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_violate_constraint_child_to_invalid(
        self, db_session: AsyncSession
    ):
        """Test updating child category to violate constraint"""
        # Create valid child category
        category = Categories(
            name="test child update violation",
            description="test description",
            parent_id=self.test_category1.id,
            category_type_id=None
        )
        await save_object(db_session, category)

        # Try to update to invalid state (both NOT NULL)
        category.category_type_id = self.test_category_type.id
        # parent_id remains set

        with pytest.raises(IntegrityError):
            await save_object(db_session, category)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_valid_update_top_level_to_child(self, db_session: AsyncSession):
        """Test valid update from top-level to child category"""
        # Create valid top-level category
        category = Categories(
            name="test top to child",
            description="test description",
            parent_id=None,
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, category)

        # Update to valid child state
        category.parent_id = self.test_category1.id
        category.category_type_id = None

        # Should succeed - no exception raised
        await save_object(db_session, category)
        assert category.parent_id == self.test_category1.id
        assert category.category_type_id is None

    @pytest.mark.asyncio
    async def test_valid_update_child_to_top_level(self, db_session: AsyncSession):
        """Test valid update from child to top-level category"""
        # Create valid child category
        category = Categories(
            name="test child to top",
            description="test description",
            parent_id=self.test_category1.id,
            category_type_id=None
        )
        await save_object(db_session, category)

        # Update to valid top-level state
        category.parent_id = None
        category.category_type_id = self.test_category_type.id

        # Should succeed - no exception raised
        await save_object(db_session, category)
        assert category.parent_id is None
        assert category.category_type_id == self.test_category_type.id

    @pytest.mark.asyncio
    async def test_invalid_self_reference_constraint(self, db_session: AsyncSession):
        """Test invalid self-reference: category cannot reference itself as parent"""
        # Create category first
        category = Categories(
            name="test self reference constraint",
            description="test description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, category)

        # Try to set itself as parent (violates constraint)
        category.parent_id = category.id
        category.category_type_id = None  # Remove to satisfy hierarchy constraint

        # Should fail with IntegrityError due to self-reference constraint violation
        with pytest.raises(IntegrityError):
            await save_object(db_session, category)
        await db_session.rollback()

    """
    ================================================
    Relationship Tests (Categories -> CategoryTypes)
    ================================================
    """

    @pytest.mark.asyncio
    async def test_category_with_category_type_relationship(
        self, db_session: AsyncSession
    ):
        """Test category with category_type relationship properly loads"""
        retrieved_category = await get_object_by_id(
            db_session,
            Categories,
            self.test_category1.id
        )

        assert retrieved_category.category_type_id == self.test_category_type.id
        assert retrieved_category.category_type == self.test_category_type
        assert retrieved_category.category_type.name == "test category type"

    @pytest.mark.asyncio
    async def test_category_without_category_type_relationship(
        self, db_session: AsyncSession
    ):
        """Test category without category_type relationship"""
        retrieved_category = await get_object_by_id(
            db_session,
            Categories,
            self.test_category2.id
        )

        assert retrieved_category.category_type_id is None
        assert retrieved_category.category_type is None

    @pytest.mark.asyncio
    async def test_update_category_to_different_category_type(
        self, db_session: AsyncSession
    ):
        """Test updating a category to use a different category_type"""
        # Create another category type
        another_category_type = CategoryTypes(
            name="another test category type"
        )
        await save_object(db_session, another_category_type)

        # Create category with first category_type
        category = Categories(
            name="test category change type",
            description="test description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, category)

        # Verify initially has first category_type
        assert category.category_type_id == self.test_category_type.id
        assert category.category_type == self.test_category_type
        assert category.category_type.name == "test category type"

        # Update to use different category_type
        category.category_type_id = another_category_type.id
        await save_object(db_session, category)

        # Verify category_type relationship is now the other one
        assert category.category_type_id == another_category_type.id
        assert category.category_type == another_category_type
        assert category.category_type.name == "another test category type"

    @pytest.mark.asyncio
    async def test_create_category_with_invalid_category_type_id(
        self, db_session: AsyncSession
    ):
        """Test creating category with non-existent category_type_id raises error"""
        category = Categories(
            name="test invalid category type",
            description="test description",
            category_type_id=999  # Non-existent ID
        )

        with pytest.raises(IntegrityError):
            await save_object(db_session, category)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_category_with_invalid_category_type_id(
        self, db_session: AsyncSession
    ):
        """Test updating category with non-existent category_type_id raises error"""
        category = Categories(
            name="test invalid update",
            description="test description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, category)

        # Update with invalid category_type_id
        category.category_type_id = 999  # Non-existent ID

        with pytest.raises(IntegrityError):
            await save_object(db_session, category)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_setting_category_type_to_null_on_top_category_fails(
        self, db_session: AsyncSession
    ):
        """Test that setting category_type_id to NULL on top-level category fails"""

        # Create valid top-level category
        category = Categories(
            name="Test Category",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, category)

        # Try to set category_type_id to NULL (should fail constraint)
        category.category_type_id = None

        with pytest.raises(IntegrityError) as exc_info:
            await save_object(db_session, category)
        await db_session.rollback()

        assert "check_category_hierarchy_rule" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_category_with_category_type_relationship(
        self, db_session: AsyncSession
    ):
        """Test deleting a category that has category_type relationship"""
        # Create category with category_type
        category = Categories(
            name="test delete with type",
            description="test description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, category)

        category_type = await get_object_by_id(
            db_session,
            CategoryTypes,
            self.test_category_type.id
        )

        await db_session.refresh(category_type, ['categories'])

        assert category_type.categories == [self.test_category1, category]

        # Delete the category
        await delete_object(db_session, category)

        # Verify category is deleted
        deleted_category = await get_object_by_id(
            db_session, Categories, category.id
        )
        assert deleted_category is None

        # Verify category_type still exists (should not be affected)
        await db_session.refresh(category_type, ['categories'])
        assert category_type is not None
        assert category_type.name == "test category type"
        assert category_type.categories == [self.test_category1]

    """
    ================================================
    Relationship Tests (Categories -> Categories)
    ================================================
    """

    @pytest.mark.asyncio
    async def test_category_with_parent_relationship(self, db_session: AsyncSession):
        """Test category with parent relationship properly loads"""
        retrieved_category = await get_object_by_id(
            db_session,
            Categories,
            self.test_category2.id
        )

        assert retrieved_category.parent_id == self.test_category1.id
        assert retrieved_category.parent == self.test_category1
        assert retrieved_category.parent.name == "test category 1"

    @pytest.mark.asyncio
    async def test_category_without_parent_relationship(
        self, db_session: AsyncSession
    ):
        """Test category without parent relationship (top-level category)"""
        retrieved_category = await get_object_by_id(
            db_session,
            Categories,
            self.test_category1.id
        )

        assert retrieved_category.parent_id is None
        assert retrieved_category.parent is None

    @pytest.mark.asyncio
    async def test_category_with_children_relationship(
        self, db_session: AsyncSession
    ):
        """Test category with children relationship properly loads"""
        retrieved_category = await get_object_by_id(
            db_session,
            Categories,
            self.test_category1.id
        )
        await db_session.refresh(retrieved_category, ['children'])

        assert len(retrieved_category.children) == 1
        assert retrieved_category.children[0] == self.test_category2
        assert retrieved_category.children[0].name == "test category 2"

    @pytest.mark.asyncio
    async def test_category_without_children_relationship(
        self, db_session: AsyncSession
    ):
        """Test category without children relationship (leaf category)"""
        retrieved_category = await get_object_by_id(
            db_session,
            Categories,
            self.test_category2.id
        )
        await db_session.refresh(retrieved_category, ['children'])

        assert len(retrieved_category.children) == 0
        assert retrieved_category.children == []

    @pytest.mark.asyncio
    async def test_create_deep_hierarchy(self, db_session: AsyncSession):
        """Test creating a deep category hierarchy"""
        # Create level 3 category
        level3_category = Categories(
            name="level 3 category",
            description="level 3 description",
            parent_id=self.test_category2.id
        )
        await save_object(db_session, level3_category)

        # Create level 4 category
        level4_category = Categories(
            name="level 4 category",
            description="level 4 description",
            parent_id=level3_category.id
        )
        await save_object(db_session, level4_category)

        # Test the hierarchy
        await db_session.refresh(level3_category, ['children'])
        await db_session.refresh(level4_category, ['children'])

        assert level4_category.parent.parent.parent == self.test_category1
        assert level4_category.parent == level3_category
        assert level4_category.children == []
        assert level3_category.parent == self.test_category2
        assert level3_category.children == [level4_category]
        assert level3_category.children[0].name == "level 4 category"

    @pytest.mark.asyncio
    async def test_update_category_to_different_parent(
        self, db_session: AsyncSession
    ):
        """Test updating a category to use a different parent"""
        # Create another top-level category to use as parent
        another_parent = Categories(
            name="another parent category",
            description="another parent description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, another_parent)

        # Create child category with first parent
        category = Categories(
            name="test change parent",
            description="test description",
            parent_id=self.test_category1.id
        )
        await save_object(db_session, category)

        # Verify initially has first parent
        assert category.parent_id == self.test_category1.id
        assert category.parent == self.test_category1
        assert category.parent.name == "test category 1"

        # Update to use different parent
        category.parent_id = another_parent.id
        await save_object(db_session, category)

        # Verify parent relationship is now the other one
        assert category.parent_id == another_parent.id
        assert category.parent == another_parent
        assert category.parent.name == "another parent category"

    @pytest.mark.asyncio
    async def test_create_category_with_invalid_parent_id(
        self, db_session: AsyncSession
    ):
        """Test creating category with non-existent parent_id raises error"""
        category = Categories(
            name="test invalid parent",
            description="test description",
            parent_id=999  # Non-existent ID
        )

        with pytest.raises(IntegrityError):
            await save_object(db_session, category)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_category_with_invalid_parent_id(
        self, db_session: AsyncSession
    ):
        """Test updating category with non-existent parent_id raises error"""
        # Create top-level category
        category = Categories(
            name="test invalid parent update",
            description="test description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, category)

        # Update with invalid parent_id
        category.parent_id = 999  # Non-existent ID
        category.category_type_id = None  # Remove to satisfy constraint

        with pytest.raises(IntegrityError):
            await save_object(db_session, category)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_setting_parent_id_to_null_on_child_category_fails(
        self, db_session: AsyncSession
    ):
        """Test that setting parent_id to NULL on child category fails"""
        # Create valid child category
        category = Categories(
            name="test child category",
            description="test description",
            parent_id=self.test_category1.id
        )
        await save_object(db_session, category)

        # Try to set parent_id to NULL (should fail constraint)
        category.parent_id = None

        with pytest.raises(IntegrityError) as exc_info:
            await save_object(db_session, category)
        await db_session.rollback()

        assert "check_category_hierarchy_rule" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_category_with_parent_relationship(
        self, db_session: AsyncSession
    ):
        """Test deleting a category that has parent relationship"""
        # Create child category
        category = Categories(
            name="test delete with parent",
            description="test description",
            parent_id=self.test_category1.id
        )
        await save_object(db_session, category)

        category_parent = await get_object_by_id(
            db_session,
            Categories,
            self.test_category1.id
        )
        await db_session.refresh(category_parent, ['children'])
        assert category_parent.children == [self.test_category2, category]

        # Delete the child category
        await delete_object(db_session, category)

        # Verify category is deleted
        deleted_category = await get_object_by_id(
            db_session, Categories, category.id
        )
        assert deleted_category is None

        await db_session.refresh(category_parent, ['children'])

        # Verify parent still exists (should not be affected)
        assert category_parent is not None
        assert category_parent.name == "test category 1"
        assert category_parent.children == [self.test_category2]

    @pytest.mark.asyncio
    async def test_delete_parent_category_with_children(
        self, db_session: AsyncSession
    ):
        """Test deleting a parent category that has children"""
        # Create additional child
        child_category = Categories(
            name="test child for deletion",
            description="test description",
            parent_id=self.test_category1.id
        )
        await save_object(db_session, child_category)

        # Verify parent has children
        parent = await get_object_by_id(
            db_session, Categories, self.test_category1.id
        )
        await db_session.refresh(parent, ['children'])
        # At least test_category2 and child_category
        assert parent.children == [self.test_category2, child_category]

        # Delete the parent category
        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            await delete_object(db_session, parent)
        await db_session.rollback()

    """
    ================================================
    Relationship Tests (Categories -> Products)
    ================================================
    """

    @pytest.fixture
    async def setup_supplier(self, db_session: AsyncSession):
        """Setup supplier for product tests"""
        if not hasattr(self, 'test_supplier'):
            self.test_supplier = Suppliers(
                name="Test Supplier Default",
                company_type="PT",
                contact="1234567890123",
                email="default@supplier.com"
            )
            await save_object(db_session, self.test_supplier)

    @pytest.mark.asyncio
    async def test_create_category_with_products(
        self, db_session: AsyncSession, setup_supplier
    ):
        """Test creating category with products (valid scenario)"""
        category = Categories(
            name="Test Category with Products",
            description="Test Description with Products",
            category_type_id=self.test_category_type.id,
            products=[
                Products(
                    name="Test Product 1",
                    description="Test Description 1",
                    supplier_id=self.test_supplier.id
                ),
                Products(
                    name="Test Product 2",
                    description="Test Description 2",
                    supplier_id=self.test_supplier.id
                )
            ]
        )
        await save_object(db_session, category)

        retrieved_category = await get_object_by_id(
            db_session,
            Categories,
            category.id
        )
        await db_session.refresh(retrieved_category, ['products'])

        assert retrieved_category.id == 3
        assert retrieved_category.name == "Test Category with Products"
        assert retrieved_category.description == "Test Description with Products"
        assert len(retrieved_category.products) == 2
        assert retrieved_category.products[0].name == "Test Product 1"
        assert retrieved_category.products[0].description == "Test Description 1"
        assert retrieved_category.products[0].slug == "test-product-1"
        assert retrieved_category.products[0].supplier_id == self.test_supplier.id

        assert retrieved_category.products[1].name == "Test Product 2"
        assert retrieved_category.products[1].description == "Test Description 2"
        assert retrieved_category.products[1].slug == "test-product-2"
        assert retrieved_category.products[1].supplier_id == self.test_supplier.id

    @pytest.mark.asyncio
    async def test_add_multiple_products_to_category(
        self, db_session: AsyncSession, setup_supplier
    ):
        """Test adding multiple products to category"""
        products = []
        for i in range(5):
            product = Products(
                name=f"Test Product {i}",
                description=f"Test Description {i}",
                category_id=self.test_category1.id,
                supplier_id=self.test_supplier.id
            )
            await save_object(db_session, product)
            products.append(product)

        retrieved_category = await get_object_by_id(
            db_session,
            Categories,
            self.test_category1.id
        )
        await db_session.refresh(retrieved_category, ['products'])

        assert len(retrieved_category.products) == 5
        for i in range(5):
            assert retrieved_category.products[i].id == i + 1
            assert retrieved_category.products[i].name == f"Test Product {i}"
            assert retrieved_category.products[i].slug == f"test-product-{i}"
            assert retrieved_category.products[i].description == f"Test Description {i}"
            assert retrieved_category.products[i].supplier_id == self.test_supplier.id

    @pytest.mark.asyncio
    async def test_category_deletion_with_products(
        self, db_session: AsyncSession, setup_supplier
    ):
        """Test what happens when trying to delete category with associated products"""
        # Create product associated with the category
        product = Products(
            name="Test Product Delete",
            category_id=self.test_category1.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, product)

        # Try to delete category that has associated products
        with pytest.raises(IntegrityError):
            await delete_object(db_session, self.test_category1)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_orphaned_product_cleanup(
        self, db_session: AsyncSession, setup_supplier
    ):
        """Test handling of products when their category is deleted"""
        # Create temporary category
        temp_category = Categories(
            name="Temporary Category",
            description="Temporary description",
            category_type_id=self.test_category_type.id
        )
        await save_object(db_session, temp_category)

        # Create product associated with temp category
        temp_product = Products(
            name="Temporary Product",
            category_id=temp_category.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, temp_product)

        # Try to delete the category (should fail due to foreign key)
        with pytest.raises(IntegrityError):
            await delete_object(db_session, temp_category)
        await db_session.rollback()

        # To properly delete, first remove the product
        await delete_object(db_session, temp_product)

        # Now category can be deleted
        await delete_object(db_session, temp_category)

        # Verify both are deleted
        deleted_product = await get_object_by_id(
            db_session, Products, temp_product.id
        )
        deleted_category = await get_object_by_id(
            db_session, Categories, temp_category.id
        )

        assert deleted_product is None
        assert deleted_category is None

    @pytest.mark.asyncio
    async def test_query_category_by_products(
        self, db_session: AsyncSession, setup_supplier
    ):
        """Test querying category by products"""
        # Create products associated with different categories
        product1 = Products(
            name="Query Product 1",
            category_id=self.test_category1.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, product1)

        product2 = Products(
            name="Query Product 2",
            category_id=self.test_category2.id,
            supplier_id=self.test_supplier.id
        )
        await save_object(db_session, product2)

        # Query category by products using raw SQL
        stmt = select(Categories).join(Products).where(
            Products.name == "Query Product 1"
        )
        result = await db_session.execute(stmt)
        category = result.scalar_one_or_none()

        assert category.id == self.test_category1.id
        assert category.name == "test category 1"
        assert category.slug == "test-category-1"
