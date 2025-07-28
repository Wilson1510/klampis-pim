from typing import Optional, List, Literal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import StrictStr
from pydantic_core import PydanticUndefined
import pytest

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema, StrictPositiveInt
)
from app.schemas.category_schema import (
    CategoryBase, CategoryCreate,
    CategoryUpdate, CategoryInDB,
    CategoryResponse, CategoryPathItem
)
from app.models.category_type_model import CategoryTypes
from app.models.category_model import Categories
from tests.utils.model_test_utils import save_object


class TestCategoryBase:
    """Test cases for the category base schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.category_dict = {
            "name": "Test Category",
            "description": "Test Category Description"
        }

    def test_category_base_schema_inheritance(self):
        """Test that the category base schema inherits from BaseSchema"""
        assert issubclass(CategoryBase, BaseSchema)

    def test_category_base_fields_inheritance(self):
        """Test that the category base schema inherits from BaseSchema"""
        fields = CategoryBase.model_fields
        assert len(fields) == 2
        assert 'name' in fields
        assert 'description' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        description = fields['description']
        assert description.is_required() is False
        assert description.annotation == Optional[str]
        assert description.default is None

    def test_category_base_schema_input(self):
        schema = CategoryBase(**self.category_dict)
        assert schema.name == "Test Category"
        assert schema.description == "Test Category Description"

    def test_category_base_schema_input_updated(self):
        schema = CategoryBase(**self.category_dict)
        assert schema.name == "Test Category"
        assert schema.description == "Test Category Description"

        schema.name = "Test Category Updated"
        assert schema.name == "Test Category Updated"

    def test_category_base_schema_model_dump(self):
        schema = CategoryBase(**self.category_dict)
        assert schema.model_dump() == {
            "name": "Test Category",
            "description": "Test Category Description"
        }

    def test_category_base_schema_model_dump_json(self):
        schema = CategoryBase(**self.category_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"Test Category",'\
            '"description":"Test Category Description"'\
            '}'


class TestCategoryCreate:
    """Test cases for the category create schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.category_dict1 = {
            "name": "Test Category 1",
            "description": "Test Category 1 Description",
            "category_type_id": 1
        }
        self.category_dict2 = {
            "name": "Test Category 2",
            "description": "Test Category 2 Description",
            "parent_id": 1
        }

    def test_category_create_schema_inheritance(self):
        """Test that the category create schema inherits from BaseCreateSchema"""
        assert issubclass(CategoryCreate, BaseCreateSchema)
        assert issubclass(CategoryCreate, CategoryBase)

    def test_category_create_fields_inheritance(self):
        """Test that the category create schema inherits from BaseCreateSchema"""
        fields = CategoryCreate.model_fields
        assert len(fields) == 7
        assert 'name' in fields
        assert 'description' in fields
        assert 'category_type_id' in fields
        assert 'parent_id' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        description = fields['description']
        assert description.is_required() is False
        assert description.annotation == Optional[str]
        assert description.default is None

        category_type_id = fields['category_type_id']
        assert category_type_id.is_required() is False
        assert category_type_id.annotation == Optional[StrictPositiveInt]
        assert category_type_id.default is None

        parent_id = fields['parent_id']
        assert parent_id.is_required() is False
        assert parent_id.annotation == Optional[StrictPositiveInt]
        assert parent_id.default is None

    def test_category_create_schema_input(self):
        schema = CategoryCreate(**self.category_dict1)
        assert schema.name == "Test Category 1"
        assert schema.description == "Test Category 1 Description"
        assert schema.category_type_id == 1
        assert schema.parent_id is None

    def test_category_create_schema_input_updated(self):
        schema = CategoryCreate(**self.category_dict2)
        assert schema.name == "Test Category 2"
        assert schema.description == "Test Category 2 Description"
        assert schema.category_type_id is None
        assert schema.parent_id == 1

        schema.name = "Test Category 2 Updated"
        assert schema.name == "Test Category 2 Updated"

    def test_category_create_schema_model_dump(self):
        schema = CategoryCreate(**self.category_dict1)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "name": "Test Category 1",
            "description": "Test Category 1 Description",
            "category_type_id": 1,
            "parent_id": None,
            "images": []
        }

    def test_category_create_schema_model_dump_json(self):
        schema = CategoryCreate(**self.category_dict2)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"name":"Test Category 2",'\
            '"description":"Test Category 2 Description",'\
            '"category_type_id":null,'\
            '"parent_id":1,'\
            '"images":[]'\
            '}'

    def test_validate_category_hierarchy(self):
        """
        Test that the category create schema validates that parent_id and
        category_type_id are not both present
        """
        parent_id_category_type_id_exist = {
            "name": "Test Category 1",
            "description": "Test Category 1 Description",
            "category_type_id": 1,
            "parent_id": 1
        }

        # Error should be raised
        with pytest.raises(ValueError):
            CategoryCreate(**parent_id_category_type_id_exist)

        parent_id_category_type_id_not_exist = {
            "name": "Test Category 1",
            "description": "Test Category 1 Description"
        }

        # Error should be raised
        with pytest.raises(ValueError):
            CategoryCreate(**parent_id_category_type_id_not_exist)

        category_type_id_parent_id_exist = {
            "name": "Test Category 1",
            "description": "Test Category 1 Description",
            "parent_id": 1
        }

        # No error should be raised
        CategoryCreate(**category_type_id_parent_id_exist)


class TestCategoryUpdate:
    """Test cases for the category update schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.category_dict = {
            "name": "Test Category",
            "description": "Test Category Description",
            "category_type_id": 1,
            "parent_id": 1
        }

    def test_category_update_schema_inheritance(self):
        """Test that the category update schema inherits from BaseUpdateSchema"""
        assert issubclass(CategoryUpdate, BaseUpdateSchema)
        assert issubclass(CategoryUpdate, CategoryBase)

    def test_category_update_fields_inheritance(self):
        """Test that the category update schema inherits from BaseUpdateSchema"""
        fields = CategoryUpdate.model_fields
        assert len(fields) == 9
        assert 'name' in fields
        assert 'description' in fields
        assert 'category_type_id' in fields
        assert 'parent_id' in fields

        name = fields['name']
        assert name.is_required() is False
        assert name.annotation == Optional[StrictStr]
        assert name.default is None
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100

        description = fields['description']
        assert description.is_required() is False
        assert description.annotation == Optional[str]
        assert description.default is None

        category_type_id = fields['category_type_id']
        assert category_type_id.is_required() is False
        assert category_type_id.annotation == Optional[StrictPositiveInt]
        assert category_type_id.default is None

        parent_id = fields['parent_id']
        assert parent_id.is_required() is False
        assert parent_id.annotation == Optional[StrictPositiveInt]
        assert parent_id.default is None

    def test_category_update_schema_input(self):
        # Error will be raised at service layer
        schema = CategoryUpdate(**self.category_dict)
        assert schema.name == "Test Category"
        assert schema.description == "Test Category Description"
        assert schema.category_type_id == 1
        assert schema.parent_id == 1

    def test_category_update_schema_input_updated(self):
        schema = CategoryUpdate(**self.category_dict)
        assert schema.name == "Test Category"
        assert schema.description == "Test Category Description"
        assert schema.category_type_id == 1
        assert schema.parent_id == 1

        schema.name = "Test Category Updated"
        assert schema.name == "Test Category Updated"

    def test_category_update_schema_model_dump(self):
        schema = CategoryUpdate(**self.category_dict)
        assert schema.model_dump() == {
            "is_active": None,
            "sequence": None,
            "name": "Test Category",
            "description": "Test Category Description",
            "category_type_id": 1,
            "parent_id": 1,
            "images_to_create": [],
            "images_to_update": [],
            "images_to_delete": []
        }

    def test_category_update_schema_model_dump_json(self):
        schema = CategoryUpdate(**self.category_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":null,'\
            '"sequence":null,'\
            '"name":"Test Category",'\
            '"description":"Test Category Description",'\
            '"category_type_id":1,'\
            '"parent_id":1,'\
            '"images_to_create":[],'\
            '"images_to_update":[],'\
            '"images_to_delete":[]'\
            '}'


class TestCategoryPathItem:
    """Test cases for the category path item schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.category_path_item_dict = {
            "name": "Test Category",
            "slug": "test-category",
            "category_type": "Test Category Type",
            "type": "Category"
        }

    def test_category_path_item_schema_inheritance(self):
        """Test that the category path item schema inherits from BaseSchema"""
        assert issubclass(CategoryPathItem, BaseSchema)

    def test_category_path_item_fields_inheritance(self):
        """Test that the category path item schema inherits from BaseSchema"""
        fields = CategoryPathItem.model_fields
        assert len(fields) == 4
        assert 'name' in fields
        assert 'slug' in fields
        assert 'category_type' in fields
        assert 'type' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        category_type = fields['category_type']
        assert category_type.is_required() is False
        assert category_type.annotation == Optional[str]
        assert category_type.default is None

        type = fields['type']
        assert type.is_required() is False
        assert type.annotation == Literal["Category"]
        assert type.default == "Category"

    def test_category_path_item_schema_input(self):
        schema = CategoryPathItem(**self.category_path_item_dict)
        assert schema.name == "Test Category"
        assert schema.slug == "test-category"
        assert schema.category_type == "Test Category Type"
        assert schema.type == "Category"

    def test_category_path_item_schema_input_updated(self):
        schema = CategoryPathItem(**self.category_path_item_dict)
        assert schema.name == "Test Category"
        assert schema.slug == "test-category"
        assert schema.category_type == "Test Category Type"
        assert schema.type == "Category"

        schema.name = "Test Category Updated"
        assert schema.name == "Test Category Updated"

    def test_category_path_item_schema_model_dump(self):
        schema = CategoryPathItem(**self.category_path_item_dict)
        assert schema.model_dump() == {
            "name": "Test Category",
            "slug": "test-category",
            "category_type": "Test Category Type",
            "type": "Category"
        }

    def test_category_path_item_schema_model_dump_json(self):
        schema = CategoryPathItem(**self.category_path_item_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"Test Category",'\
            '"slug":"test-category",'\
            '"category_type":"Test Category Type",'\
            '"type":"Category"'\
            '}'


class TestCategoryInDB:
    """Test cases for the category in db schema"""

    def test_category_in_db_inheritance(self):
        """Test that the category in db schema inherits from BaseInDB"""
        assert issubclass(CategoryInDB, BaseInDB)
        assert issubclass(CategoryInDB, CategoryBase)

    def test_category_in_db_fields_inheritance(self):
        """Test that the category in db schema inherits from BaseInDB"""
        fields = CategoryInDB.model_fields
        assert len(fields) == 13
        assert 'name' in fields
        assert 'description' in fields
        assert 'slug' in fields
        assert 'category_type_id' in fields
        assert 'parent_id' in fields
        assert 'children' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        description = fields['description']
        assert description.is_required() is False
        assert description.annotation == Optional[str]
        assert description.default is None

        category_type_id = fields['category_type_id']
        assert category_type_id.is_required() is False
        assert category_type_id.annotation == Optional[int]
        assert category_type_id.default is None

        parent_id = fields['parent_id']
        assert parent_id.is_required() is False
        assert parent_id.annotation == Optional[int]
        assert parent_id.default is None

        children = fields['children']
        assert children.is_required() is False
        assert children.annotation == List[CategoryInDB]
        assert children.default is PydanticUndefined

        model_config = CategoryInDB.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_category_in_db_model_validate(self, db_session: AsyncSession):
        """Test that the category in db schema model validate"""
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        model = Categories(name="Parent Category", category_type_id=category_type.id)
        await save_object(db_session, model)

        child_category = Categories(name="Child Category", parent_id=model.id)
        await save_object(db_session, child_category)

        grand_child_category = Categories(
            name="Grand Child Category",
            parent_id=child_category.id
        )
        await save_object(db_session, grand_child_category)

        query = (
            select(Categories)
            .where(Categories.id == model.id)
            .options(
                selectinload(Categories.children)
                .selectinload(Categories.children)
                .selectinload(Categories.children)
            )
        )
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = CategoryInDB.model_validate(db_model)
        assert db_schema_object == CategoryInDB(
            id=model.id,
            name="Parent Category",
            slug="parent-category",
            description=None,
            category_type_id=category_type.id,
            parent_id=None,
            children=[
                CategoryInDB(
                    id=child_category.id,
                    name="Child Category",
                    slug="child-category",
                    description=None,
                    category_type_id=None,
                    parent_id=model.id,
                    children=[
                        CategoryInDB(
                            id=grand_child_category.id,
                            name="Grand Child Category",
                            slug="grand-child-category",
                            description=None,
                            category_type_id=None,
                            parent_id=child_category.id,
                            children=[],
                            created_at=grand_child_category.created_at,
                            updated_at=grand_child_category.updated_at,
                            created_by=grand_child_category.created_by,
                            updated_by=grand_child_category.updated_by,
                            is_active=True,
                            sequence=0
                        )
                    ],
                    created_at=child_category.created_at,
                    updated_at=child_category.updated_at,
                    created_by=child_category.created_by,
                    updated_by=child_category.updated_by,
                    is_active=True,
                    sequence=0
                )
            ],
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )

    @pytest.mark.asyncio
    async def test_category_in_db_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the category in db schema model validate updated"""
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        model = Categories(name="Parent Category", category_type_id=category_type.id)
        await save_object(db_session, model)

        child_category = Categories(name="Child Category", parent_id=model.id)
        await save_object(db_session, child_category)

        grand_child_category = Categories(
            name="Grand Child Category",
            parent_id=child_category.id
        )
        await save_object(db_session, grand_child_category)

        query = (
            select(Categories)
            .where(Categories.id == model.id)
            .options(
                selectinload(Categories.children)
                .selectinload(Categories.children)
                .selectinload(Categories.children)
            )
        )
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Parent Category Updated"
        db_model.children[0].name = "Child Category Updated"
        db_model.children[0].children[0].name = "Grand Child Category Updated"

        db_schema_object = CategoryInDB.model_validate(db_model)
        assert db_schema_object == CategoryInDB(
            id=model.id,
            name="Parent Category Updated",
            slug="parent-category-updated",
            description=None,
            category_type_id=category_type.id,
            parent_id=None,
            children=[
                CategoryInDB(
                    id=child_category.id,
                    name="Child Category Updated",
                    slug="child-category-updated",
                    description=None,
                    category_type_id=None,
                    parent_id=model.id,
                    children=[
                        CategoryInDB(
                            id=grand_child_category.id,
                            name="Grand Child Category Updated",
                            slug="grand-child-category-updated",
                            description=None,
                            category_type_id=None,
                            parent_id=child_category.id,
                            children=[],
                            created_at=grand_child_category.created_at,
                            updated_at=grand_child_category.updated_at,
                            created_by=grand_child_category.created_by,
                            updated_by=grand_child_category.updated_by,
                            is_active=True,
                            sequence=0
                        )
                    ],
                    created_at=child_category.created_at,
                    updated_at=child_category.updated_at,
                    created_by=child_category.created_by,
                    updated_by=child_category.updated_by,
                    is_active=True,
                    sequence=0
                )
            ],
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )


class TestCategoryResponse:
    """Test cases for the category response schema"""

    def test_category_response_inheritance(self):
        """Test that the category response schema inherits from CategoryInDB"""
        assert issubclass(CategoryResponse, CategoryInDB)

    def test_category_response_fields_inheritance(self):
        """Test that the category response schema inherits from CategoryInDB"""
        fields = CategoryResponse.model_fields
        assert len(fields) == 15
        assert 'name' in fields
        assert 'description' in fields
        assert 'slug' in fields
        assert 'category_type_id' in fields
        assert 'parent_id' in fields
        assert 'children' in fields
        assert 'full_path' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 100
        assert name.metadata[2].strict is True

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        description = fields['description']
        assert description.is_required() is False
        assert description.annotation == Optional[str]
        assert description.default is None

        category_type_id = fields['category_type_id']
        assert category_type_id.is_required() is False
        assert category_type_id.annotation == Optional[int]
        assert category_type_id.default is None

        parent_id = fields['parent_id']
        assert parent_id.is_required() is False
        assert parent_id.annotation == Optional[int]
        assert parent_id.default is None

        children = fields['children']
        assert children.is_required() is False
        assert children.annotation == List[CategoryResponse]
        assert children.default is PydanticUndefined

        full_path = fields['full_path']
        assert full_path.is_required() is True
        assert full_path.annotation == List[CategoryPathItem]
        assert full_path.default is PydanticUndefined

        model_config = CategoryInDB.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_category_response_model_validate(self, db_session: AsyncSession):
        """Test that the category response schema model validate"""
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        model = Categories(
            name="Parent Category",
            category_type_id=category_type.id
        )
        await save_object(db_session, model)

        child_category = Categories(name="Child Category", parent_id=model.id)
        await save_object(db_session, child_category)

        query = select(Categories).where(Categories.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()
        await db_session.refresh(db_model, ['children', 'images'])
        for child in db_model.children:
            await db_session.refresh(child, ['children', 'images'])

        db_schema_object = CategoryResponse.model_validate(db_model)

        assert db_schema_object == CategoryResponse(
            id=model.id,
            name="Parent Category",
            slug="parent-category",
            description=None,
            category_type_id=category_type.id,
            parent_id=None,
            children=[
                CategoryResponse(
                    id=child_category.id,
                    name="Child Category",
                    slug="child-category",
                    description=None,
                    category_type_id=None,
                    parent_id=model.id,
                    children=[],
                    full_path=[
                        CategoryPathItem(
                            name="Parent Category",
                            slug="parent-category",
                            category_type=category_type.name,
                            type="Category"
                        ),
                        CategoryPathItem(
                            name="Child Category",
                            slug="child-category",
                            category_type=None,
                            type="Category"
                        )
                    ],
                    images=[],
                    created_at=child_category.created_at,
                    updated_at=child_category.updated_at,
                    created_by=child_category.created_by,
                    updated_by=child_category.updated_by,
                    is_active=True,
                    sequence=0
                )
            ],
            full_path=[
                CategoryPathItem(
                    name="Parent Category",
                    slug="parent-category",
                    category_type=category_type.name,
                    type="Category"
                )
            ],
            images=[],
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )

    @pytest.mark.asyncio
    async def test_category_response_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the category response schema model validate updated"""
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        model = Categories(
            name="Parent Category",
            category_type_id=category_type.id
        )
        await save_object(db_session, model)

        child_category = Categories(name="Child Category", parent_id=model.id)
        await save_object(db_session, child_category)

        query = select(Categories).where(Categories.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        await db_session.refresh(db_model, ['children', 'images'])
        for child in db_model.children:
            await db_session.refresh(child, ['children', 'images'])

        db_model.full_path[0]['name'] = "Full Path Parent Category Updated"
        db_model.children[0].full_path[0]['name'] = "Full Path Child Category Updated"

        # Full path is just a property. Even if we update the full path, when model
        # validate is called, the full path will be recomputed and got normal value

        db_schema_object = CategoryResponse.model_validate(db_model)
        assert db_schema_object == CategoryResponse(
            id=model.id,
            name="Parent Category",
            slug="parent-category",
            description=None,
            category_type_id=category_type.id,
            parent_id=None,
            children=[
                CategoryResponse(
                    id=child_category.id,
                    name="Child Category",
                    slug="child-category",
                    description=None,
                    category_type_id=None,
                    parent_id=model.id,
                    children=[],
                    full_path=[
                        CategoryPathItem(
                            name="Parent Category",
                            slug="parent-category",
                            category_type=category_type.name,
                            type="Category"
                        ),
                        CategoryPathItem(
                            name="Child Category",
                            slug="child-category",
                            category_type=None,
                            type="Category"
                        )
                    ],
                    images=[],
                    created_at=child_category.created_at,
                    updated_at=child_category.updated_at,
                    created_by=child_category.created_by,
                    updated_by=child_category.updated_by,
                    is_active=True,
                    sequence=0
                )
            ],
            full_path=[
                CategoryPathItem(
                    name="Parent Category",
                    slug="parent-category",
                    category_type=category_type.name,
                    type="Category"
                )
            ],
            images=[],
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )
