from sqlalchemy import (
    String, event, Text, Integer, CheckConstraint, select, Boolean, ForeignKey
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import hybrid_property
import pytest

from app.core.base import Base
from app.models.category_type_model import CategoryTypes
from app.models.category_model import Categories
from app.models.product_model import Products
from app.models.attribute_set_model import AttributeSets
from app.models.image_model import Images
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    assert_relationship,
    count_model_objects
)


@pytest.fixture
async def setup_images(image_factory, category_factory, product_factory):
    """
    Fixture to create images ONCE for the entire test module.
    This is the efficient part.
    """
    category = await category_factory()
    product = await product_factory()
    image1 = await image_factory(
        file="test_folder/test1.jpg",
        object_id=category.id,
        content_type="categories"
    )
    image2 = await image_factory(
        file="test_folder/test2.jpg",
        title="Test Image 2",
        is_primary=True,
        object_id=product.id,
        content_type="products"
    )
    return category, product, image1, image2


class TestImage:
    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_images):
        self.test_category, self.test_product, self.test_image1, \
            self.test_image2 = setup_images

    def test_inheritance_from_base_model(self):
        assert issubclass(Images, Base)

    def test_fields_with_validation(self):
        assert hasattr(Images, 'validate_file')
        assert 'file' in Images.__mapper__.validators
        assert len(Images.__mapper__.validators) == 1

    def test_has_get_parent_method(self):
        assert hasattr(Images, 'get_parent')

    def test_file_field_properties(self):
        file_column = Images.__table__.columns.get('file')
        assert file_column is not None
        assert isinstance(file_column.type, String)
        assert file_column.type.length == 255
        assert file_column.nullable is False
        assert file_column.unique is True
        assert file_column.index is None
        assert file_column.default is None

    def test_title_field_properties(self):
        title_column = Images.__table__.columns.get('title')
        assert title_column is not None
        assert isinstance(title_column.type, String)
        assert title_column.type.length == 100
        assert title_column.nullable is True
        assert title_column.unique is None
        assert title_column.index is None
        assert title_column.default is None

    def test_is_primary_field_properties(self):
        is_primary_column = Images.__table__.columns.get('is_primary')
        assert is_primary_column is not None
        assert isinstance(is_primary_column.type, Boolean)
        assert is_primary_column.nullable is False
        assert is_primary_column.unique is None
        assert is_primary_column.index is None
        assert is_primary_column.default.arg is False

    def test_object_id_field_properties(self):
        object_id_column = Images.__table__.columns.get('object_id')
        assert object_id_column is not None
        assert isinstance(object_id_column.type, Integer)
        assert object_id_column.nullable is False
        assert object_id_column.unique is None
        assert object_id_column.index is True
        assert object_id_column.default is None

    def test_content_type_field_properties(self):
        content_type_column = Images.__table__.columns.get('content_type')
        assert content_type_column is not None
        assert isinstance(content_type_column.type, String)
        assert content_type_column.type.length == 50
        assert content_type_column.nullable is False
        assert content_type_column.unique is None
        assert content_type_column.index is True
        assert content_type_column.default is None

    def test_str_representation(self):
        assert str(self.test_image1) == "Images(test_folder/test1.jpg)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        assert self.test_image1.id == 1
        assert self.test_image1.file == "test_folder/test1.jpg"
        assert self.test_image1.title is None
        assert self.test_image1.is_primary is False
        assert self.test_image1.object_id == 1
        assert self.test_image1.content_type == 'categories'
        parent = await self.test_image1.get_parent(db_session)
        assert parent == self.test_category

        assert self.test_image2.id == 2
        assert self.test_image2.file == "test_folder/test2.jpg"
        assert self.test_image2.title == "Test Image 2"
        assert self.test_image2.is_primary is True
        assert self.test_image2.object_id == 1
        assert self.test_image2.content_type == 'products'
        parent = await self.test_image2.get_parent(db_session)
        assert parent == self.test_product

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = Images(
            file="test_folder/test3.jpg",
            object_id=self.test_category.id,
            content_type="categories"
        )
        await save_object(db_session, item)

        assert item.id == 3
        assert item.file == "test_folder/test3.jpg"
        assert item.title is None
        assert item.is_primary is False
        assert item.object_id == 1
        assert item.content_type == 'categories'
        parent = await item.get_parent(db_session)
        assert parent == self.test_category
        assert parent.name == "Test Category"
        assert await count_model_objects(db_session, Images) == 3

        item = Images(
            file="test_folder/test4.jpg",
            title="Test Image 4",
            is_primary=True,
            object_id=self.test_product.id,
            content_type="products"
        )
        await save_object(db_session, item)
        assert item.id == 4
        assert item.file == "test_folder/test4.jpg"
        assert item.title == "Test Image 4"
        assert item.is_primary is True
        assert item.object_id == 1
        assert item.content_type == 'products'
        parent = await item.get_parent(db_session)
        assert parent == self.test_product
        assert parent.name == "Test Product"
        assert await count_model_objects(db_session, Images) == 4

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(db_session, Images, self.test_image1.id)
        assert item.id == 1
        assert item.file == "test_folder/test1.jpg"
        assert item.title is None
        assert item.is_primary is False
        assert item.object_id == 1
        assert item.content_type == 'categories'
        parent = await item.get_parent(db_session)
        assert parent == self.test_category
        assert parent.name == "Test Category"
        assert await count_model_objects(db_session, Images) == 2

        item = await get_object_by_id(db_session, Images, self.test_image2.id)
        assert item.id == 2
        assert item.file == "test_folder/test2.jpg"
        assert item.title == "Test Image 2"
        assert item.is_primary is True
        assert item.object_id == 1
        assert item.content_type == 'products'
        parent = await item.get_parent(db_session)
        assert parent == self.test_product
        assert parent.name == "Test Product"
        assert await count_model_objects(db_session, Images) == 2

        items = await get_all_objects(db_session, Images)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].file == "test_folder/test1.jpg"
        assert items[0].title is None
        assert items[0].is_primary is False
        assert items[0].object_id == 1
        assert items[0].content_type == 'categories'
        parent = await items[0].get_parent(db_session)
        assert parent == self.test_category
        assert parent.name == "Test Category"

        assert items[1].id == 2
        assert items[1].file == "test_folder/test2.jpg"
        assert items[1].title == "Test Image 2"
        assert items[1].is_primary is True
        assert items[1].object_id == 1
        assert items[1].content_type == 'products'
        parent = await items[1].get_parent(db_session)
        assert parent == self.test_product
        assert parent.name == "Test Product"

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession, product_factory):
        """Test the update operation"""
        item = await get_object_by_id(db_session, Images, self.test_image1.id)
        item.file = "Updated Test Image 1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.file == "Updated Test Image 1"
        assert item.title is None
        assert item.is_primary is False
        assert item.object_id == 1
        assert item.content_type == 'categories'
        parent = await item.get_parent(db_session)
        assert parent == self.test_category
        assert parent.name == "Test Category"
        assert await count_model_objects(db_session, Images) == 2

        product = await product_factory(name="Another Product")
        item.object_id = product.id
        await save_object(db_session, item)
        assert item.id == 1
        assert item.file == "Updated Test Image 1"
        assert item.object_id == 2
        assert item.title is None
        assert item.content_type == 'categories'
        parent = await item.get_parent(db_session)
        assert parent is None  # No category found with id 2
        assert await count_model_objects(db_session, Images) == 2

        item.content_type = "products"
        await save_object(db_session, item)
        assert item.id == 1
        assert item.file == "Updated Test Image 1"
        assert item.object_id == 2
        assert item.title is None
        assert item.content_type == 'products'
        parent = await item.get_parent(db_session)
        assert parent == product
        assert parent.name == "Another Product"
        assert await count_model_objects(db_session, Images) == 2

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_image1)

        item = await get_object_by_id(db_session, Images, self.test_image1.id)
        assert item is None
        assert await count_model_objects(db_session, Images) == 1
