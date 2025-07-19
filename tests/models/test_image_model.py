from sqlalchemy import (
    String, Integer, Boolean, text, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
import pytest

from app.core.base import Base
from app.models.image_model import Images
from app.models.category_model import Categories
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
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
        assert hasattr(Images, 'validate_content_type')
        assert 'file' in Images.__mapper__.validators
        assert 'content_type' in Images.__mapper__.validators
        assert len(Images.__mapper__.validators) == 2

    def test_has_listeners(self):
        assert event.contains(Base, 'class_instrument', Images.on_class_instrument)
        assert not event.contains(
            Images,
            'class_instrument',
            Images.on_class_instrument
        )

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

    def test_content_type_to_class_mapping(self):
        assert Images.CONTENT_TYPE_TO_CLASS == {
            'categories': self.test_category.__class__,
            'products': self.test_product.__class__
        }

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


class TestImageValidationDatabase:
    """Test suite for Image model database validation"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_images):
        self.test_category, self.test_product, self.test_image1, \
            self.test_image2 = setup_images

    @pytest.mark.asyncio
    async def test_valid_file_database_constraint(self, db_session: AsyncSession):
        """Test valid file passes database constraint"""
        valid_files = [
            "test_folder/test3.jpg",
            "a**&&/>n",
            "Name.jpg",
            "    test.jpg    ",
            "R12345.png",
            "test_folder/test5.aaa",
        ]

        for input_file in valid_files:
            sql = text("""
                INSERT INTO images (
                       file,
                       object_id,
                       content_type,
                       is_primary,
                       is_active,
                       sequence,
                       created_by,
                       updated_by
                )
                VALUES (
                       :file,
                       :object_id,
                       :content_type,
                       :is_primary,
                       :is_active,
                       :sequence,
                       :created_by,
                       :updated_by
                )
            """)

            # This should fail at database level due to CheckConstraint
            await db_session.execute(sql, {
                'file': input_file,
                'object_id': self.test_category.id,
                'content_type': 'categories',
                'is_active': True,
                'is_primary': False,
                'sequence': 1,
                'created_by': 1,  # System user ID
                'updated_by': 1   # System user ID
            })
            await db_session.commit()

            # Check if the image is created
            stmt = select(Images).where(Images.file == input_file)
            result = await db_session.execute(stmt)
            image = result.scalar_one_or_none()
            assert image.file == input_file

    @pytest.mark.asyncio
    async def test_invalid_file_database_constraint(self, db_session: AsyncSession):
        """Test invalid file fails database constraint"""
        # Test files that don't start with letter - should fail at database level
        invalid_files = [
            "    ",
            "",
            "1234567890",
            "  *&^%$#@!~ ",
            "^test_folder/test6.jpg ",
        ]
        category_id = self.test_category.id

        for invalid_file in invalid_files:
            # Use raw SQL to bypass application validation and test database constraint
            sql = text("""
                INSERT INTO images (
                       file,
                       object_id,
                       content_type,
                       is_primary,
                       is_active,
                       sequence,
                       created_by,
                       updated_by
                )
                VALUES (
                       :file,
                       :object_id,
                       :content_type,
                       :is_primary,
                       :is_active,
                       :sequence,
                       :created_by,
                       :updated_by
                )
            """)

            # This should fail at database level due to CheckConstraint
            with pytest.raises(
                IntegrityError, match="check_images_file_starts_with_letter"
            ):
                await db_session.execute(sql, {
                    'file': invalid_file,
                    'object_id': category_id,
                    'content_type': 'categories',
                    'is_active': True,
                    'is_primary': False,
                    'sequence': 1,
                    'created_by': 1,  # System user ID
                    'updated_by': 1   # System user ID
                })
            await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_file_invalid_database_constraint(
        self, db_session: AsyncSession
    ):
        """Test updating file with invalid value fails database constraint"""
        # Create valid image first
        image = Images(
            file="valid_test.jpg",
            object_id=self.test_category.id,
            content_type="categories"
        )
        await save_object(db_session, image)

        image_id = image.id

        invalid_files = [
            "   ",
            "",
            "1234567890",
            "  *&^%$#@!~",
            "^test_folder/test6.jpg ",
        ]

        # Try to update with invalid file name using raw SQL to bypass
        # application validation
        for invalid_file in invalid_files:
            sql = text("""
                UPDATE images
                SET file = :new_file
                WHERE id = :image_id
            """)

            with pytest.raises(
                IntegrityError, match="check_images_file_starts_with_letter"
            ):
                await db_session.execute(sql, {
                    'new_file': invalid_file,
                    'image_id': image_id
                })
            await db_session.rollback()


class TestImageValidationApplication:
    """Test suite for Image model validation"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_images):
        self.test_category, self.test_product, self.test_image1, \
            self.test_image2 = setup_images

    def test_valid_file_validation(self):
        """Test valid file validation"""
        valid_files = [
            ("test_folder/test3.jpg", "test_folder/test3.jpg"),
            ("a**&&/>n", "a**&&/>n"),
            ("Name.jpg", "Name.jpg"),
            ("    test.jpg    ", "test.jpg"),
            ("R12345.png", "R12345.png"),
            ("test_folder/test5.aaa", "test_folder/test5.aaa"),
        ]
        for input_file, expected_file in valid_files:
            item = Images(
                file=input_file,
                object_id=self.test_category.id,
                content_type="categories"
            )
            assert item.file == expected_file

    def test_invalid_file_validation(self):
        """Test invalid file validation"""
        invalid_files = [
            ("   ", "Column file cannot be empty"),
            ("", "Column file cannot be empty"),
            ("1234567890", "Column file must start with a letter"),
            ("*&^%$#@!~", "Column file must start with a letter"),
            ("^test_folder/test6.jpg", "Column file must start with a letter"),
        ]
        category_id = self.test_category.id
        for input_file, expected_error in invalid_files:
            with pytest.raises(ValueError, match=expected_error):
                Images(
                    file=input_file,
                    object_id=category_id,
                    content_type="categories"
                )

    def test_update_file_invalid_validation(self):
        """Test invalid file validation"""
        invalid_files = [
            ("   ", "Column file cannot be empty"),
            ("", "Column file cannot be empty"),
            ("1234567890", "Column file must start with a letter"),
            ("*&^%$#@!~", "Column file must start with a letter"),
            ("^test_folder/test6.jpg", "Column file must start with a letter"),
        ]
        category_id = self.test_category.id

        image = Images(
            file="test_folder/test3.jpg",
            object_id=category_id,
            content_type="categories"
        )

        for input_file, expected_error in invalid_files:
            with pytest.raises(ValueError, match=expected_error):
                image.file = input_file

    def test_valid_content_type_validation(self):
        """Test valid content type validation"""
        valid_content_types = [
            ("categories", "categories"),
            ("products", "products"),
            ("  categories", "categories"),
            ("products  ", "products"),
            ("  products  ", "products"),
        ]
        for i, (input_content_type, expected_content_type) in enumerate(
            valid_content_types, 3
        ):
            image = Images(
                file=f"test_folder/test{i}.jpg",
                object_id=self.test_category.id,
                content_type=input_content_type
            )
            assert image.content_type == expected_content_type

    def test_invalid_content_type_validation(self):
        """Test invalid content type validation"""
        invalid_content_types = [
            (
                "skus",
                "Invalid content_type: skus. Must be one of",
            ),
            (
                "  suppliers  ",
                "Invalid content_type: suppliers. Must be one of",
            ),
        ]
        category_id = self.test_category.id
        for input_content_type, expected_error in invalid_content_types:
            with pytest.raises(ValueError, match=expected_error):
                Images(
                    file="test_folder/test7.jpg",
                    object_id=category_id,
                    content_type=input_content_type
                )

    def test_update_content_type_invalid_validation(self):
        """Test updating content type validation"""
        invalid_content_types = [
            ("  skus  ", "Invalid content_type: skus. Must be one of"),
            ("suppliers", "Invalid content_type: suppliers. Must be one of"),
        ]
        category_id = self.test_category.id
        image = Images(
            file="test_folder/test3.jpg",
            object_id=category_id,
            content_type="categories"
        )
        for input_content_type, expected_error in invalid_content_types:
            with pytest.raises(ValueError, match=expected_error):
                image.content_type = input_content_type


class TestImageOtherModelRelationship:
    """
    Test suite for Image model relationships with other model that has relationship
    with Image model.
    In this testing, we use Category as the other model. It will work the same for
    other models.
    """
    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_images):
        self.test_category, self.test_product, self.test_image1, \
            self.test_image2 = setup_images

    @pytest.mark.asyncio
    async def test_image_with_other_model_relationship(self, db_session: AsyncSession):
        """Test image with other model relationship properly loads"""
        retrieved_image = await get_object_by_id(
            db_session, Images, self.test_image1.id
        )
        assert retrieved_image.object_id == self.test_category.id
        parent = await retrieved_image.get_parent(db_session)
        assert parent == self.test_category
        assert parent.name == "Test Category"

    @pytest.mark.asyncio
    async def test_image_without_other_model_relationship(
        self, db_session: AsyncSession
    ):
        """Test image without object_id and content_type"""
        product_id = self.test_product.id
        item = Images(file="test_folder/test8.jpg")
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)
        await db_session.rollback()

        """Test image with other content_type"""
        item = Images(
            file="test_folder/test9.jpg",
            object_id=product_id,
            content_type="products"
        )
        # Should not raise an error because the object_id and content_type are provided
        await save_object(db_session, item)
        assert await count_model_objects(db_session, Images) == 3

    @pytest.mark.asyncio
    async def test_update_image_to_different_other_model(
        self, db_session: AsyncSession, category_factory
    ):
        """Test updating image to use a different category"""
        another_category = await category_factory(
            name="another test category",
            description="another test category description"
        )
        image = Images(
            file="test_folder/test10.jpg",
            object_id=self.test_category.id,
            content_type="categories"
        )
        await save_object(db_session, image)
        assert image.object_id == self.test_category.id
        assert image.content_type == "categories"
        parent = await image.get_parent(db_session)
        assert parent == self.test_category
        assert parent.name == "Test Category"

        image.object_id = another_category.id
        await save_object(db_session, image)
        assert image.object_id == another_category.id
        assert image.content_type == "categories"
        parent = await image.get_parent(db_session)
        assert parent == another_category
        assert parent.name == "another test category"

    @pytest.mark.asyncio
    async def test_create_image_with_invalid_other_model_id(
        self, db_session: AsyncSession
    ):
        """Test creating image with invalid other model id"""
        image = Images(
            file="test_folder/test11.jpg",
            object_id=999,
            content_type="categories"
        )

        # Should not raise an error, validation will be handled in service layer
        await save_object(db_session, image)
        assert image.object_id == 999
        assert image.content_type == "categories"
        parent = await image.get_parent(db_session)
        assert parent is None
        assert await count_model_objects(db_session, Images) == 3

    @pytest.mark.asyncio
    async def test_update_image_with_invalid_other_model_id(
        self, db_session: AsyncSession
    ):
        """Test updating image with invalid other model id"""
        image = Images(
            file="test_folder/test12.jpg",
            object_id=self.test_category.id,
            content_type="categories"
        )
        await save_object(db_session, image)

        image.object_id = 999
        await save_object(db_session, image)
        assert image.object_id == 999
        assert image.content_type == "categories"
        parent = await image.get_parent(db_session)
        assert parent is None
        assert await count_model_objects(db_session, Images) == 3

    @pytest.mark.asyncio
    async def test_setting_object_id_to_null_fails(self, db_session: AsyncSession):
        """Test setting object_id to null fails"""
        image = Images(
            file="test_folder/test13.jpg",
            object_id=self.test_category.id,
            content_type="categories"
        )
        await save_object(db_session, image)

        image.object_id = None
        with pytest.raises(IntegrityError):
            await save_object(db_session, image)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_image_with_other_model_relationship(
        self, db_session: AsyncSession
    ):
        """Test deleting image with other model relationship"""
        image = Images(
            file="test_folder/test14.jpg",
            object_id=self.test_category.id,
            content_type="categories"
        )
        await save_object(db_session, image)

        category = await get_object_by_id(
            db_session,
            Categories,
            self.test_category.id
        )
        await db_session.refresh(category, ['images'])

        category_images = category.images
        assert category_images == [self.test_image1, image]

        await delete_object(db_session, image)

        deleted_image = await get_object_by_id(
            db_session, Images, image.id
        )
        assert deleted_image is None

        # Verify category still exists (should not be affected)
        await db_session.refresh(category, ['images'])
        assert category is not None
        assert category.name == "Test Category"
        category_images = category.images
        assert category_images == [self.test_image1]
