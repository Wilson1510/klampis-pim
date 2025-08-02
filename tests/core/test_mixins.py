import pytest
from sqlalchemy import Column, String, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError

from app.core.base import Base
from app.models import Images
from app.utils.mixins import Imageable
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    delete_object
)


class SimpleModelWithImageable(Base, Imageable):
    """Simple model with Imageable mixin."""
    name = Column(String(50), nullable=False)


@pytest.fixture
async def setup_objects(db_session: AsyncSession):
    """Setup objects for testing."""
    simple_model1 = SimpleModelWithImageable(name="Test Model 1")
    await save_object(db_session, simple_model1)

    simple_model2 = SimpleModelWithImageable(name="Test Model 2")
    await save_object(db_session, simple_model2)

    return simple_model1, simple_model2


class TestImageableMixin:
    """Test suite for Imageable mixin."""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_objects):
        """Setup objects for testing."""
        self.simple_model1, self.simple_model2 = setup_objects

    """
    ================================================================
    Test images attribute usage and its relationship with other models
    ================================================================
    """
    @pytest.mark.asyncio
    async def test_create_model_with_images(self, db_session: AsyncSession):
        """Test creating model with images (valid scenario)"""
        model = SimpleModelWithImageable(
            name="Test Model with Images",
            images=[Images(file="test image 1"), Images(file="test image 2")]
        )
        await save_object(db_session, model)

        retrieved_model = await get_object_by_id(
            db_session,
            SimpleModelWithImageable,
            model.id
        )
        await db_session.refresh(retrieved_model, ['images'])

        assert retrieved_model.id == 3
        assert retrieved_model.name == "Test Model with Images"
        assert len(retrieved_model.images) == 2

        assert retrieved_model.images[0].file == "test image 1"
        assert retrieved_model.images[0].is_primary is False
        assert retrieved_model.images[0].title is None
        assert retrieved_model.images[0].object_id == retrieved_model.id
        assert retrieved_model.images[0].content_type == "simple_model_with_imageable"
        parent = await retrieved_model.images[0].get_parent(db_session)
        assert parent == retrieved_model

        assert retrieved_model.images[1].file == "test image 2"
        assert retrieved_model.images[1].is_primary is False
        assert retrieved_model.images[1].title is None
        assert retrieved_model.images[1].object_id == retrieved_model.id
        assert retrieved_model.images[1].content_type == "simple_model_with_imageable"
        parent = await retrieved_model.images[1].get_parent(db_session)
        assert parent == retrieved_model

    @pytest.mark.asyncio
    async def test_add_multiple_images_to_model(self, db_session: AsyncSession):
        """Test adding multiple images to model"""
        for i in range(5):
            image = Images(
                file=f"test image {i}",
                object_id=self.simple_model1.id,
                content_type="simple_model_with_imageable"
            )
            await save_object(db_session, image)

        retrieved_model = await get_object_by_id(
            db_session,
            SimpleModelWithImageable,
            self.simple_model1.id
        )
        await db_session.refresh(retrieved_model, ['images'])

        assert len(retrieved_model.images) == 5
        for i in range(5):
            assert retrieved_model.images[i].id == i + 1
            assert retrieved_model.images[i].file == f"test image {i}"
            assert retrieved_model.images[i].is_primary is False
            assert retrieved_model.images[i].title is None
            assert retrieved_model.images[i].object_id == retrieved_model.id
            assert retrieved_model.images[i].content_type == (
                "simple_model_with_imageable"
            )
            parent = await retrieved_model.images[i].get_parent(db_session)
            assert parent == retrieved_model

    @pytest.mark.asyncio
    async def test_update_model_images(self, db_session: AsyncSession):
        """Test updating a model's images"""
        model = await get_object_by_id(
            db_session,
            SimpleModelWithImageable,
            self.simple_model1.id
        )
        await db_session.refresh(model, ['images'])
        assert len(model.images) == 0

        model.images = [Images(file="test image 1"), Images(file="test image 2")]
        await save_object(db_session, model)
        await db_session.refresh(model, ['images'])
        assert len(model.images) == 2

        assert model.images[0].file == "test image 1"
        parent = await model.images[0].get_parent(db_session)
        assert parent == model
        assert model.images[1].file == "test image 2"
        parent = await model.images[1].get_parent(db_session)
        assert parent == model

        model.images = [
            Images(file="test image 3"),
            Images(file="test image 4"),
            Images(file="test image 5")
        ]

        await save_object(db_session, model)
        await db_session.refresh(model, ['images'])
        assert len(model.images) == 3
        assert model.images[0].file == "test image 3"
        assert model.images[1].file == "test image 4"
        assert model.images[2].file == "test image 5"

        query = select(Images).where(
            Images.file.in_(["test image 1", "test image 2"])
        )
        result = await db_session.execute(query)
        images = result.scalars().all()
        assert len(images) == 0

    @pytest.mark.asyncio
    async def test_model_deletion_with_images(self, db_session: AsyncSession):
        """Test what happens when trying to delete model with associated images"""
        # Create image associated with the model
        image = Images(
            file="Test Image Delete",
            object_id=self.simple_model1.id,
            content_type="simple_model_with_imageable"
        )
        await save_object(db_session, image)

        await delete_object(db_session, self.simple_model1)
        assert await get_object_by_id(db_session, Images, image.id) is None

    @pytest.mark.asyncio
    async def test_query_model_by_images(self, db_session: AsyncSession):
        """Test querying model by images"""
        # Create images associated with different models
        image1 = Images(
            file="Query Image 1",
            object_id=self.simple_model1.id,
            content_type="simple_model_with_imageable"
        )
        await save_object(db_session, image1)

        image2 = Images(
            file="Query Image 2",
            object_id=self.simple_model2.id,
            content_type="simple_model_with_imageable"
        )
        await save_object(db_session, image2)

        # Query model by images using raw SQL
        stmt = select(SimpleModelWithImageable).join(
            Images,
            and_(
                SimpleModelWithImageable.id == Images.object_id,
                Images.content_type == "simple_model_with_imageable"
            )
        ).where(
            Images.file == "Query Image 1"
        )
        result = await db_session.execute(stmt)
        model = result.scalar_one_or_none()

        assert model.id == self.simple_model1.id
        assert model.name == "Test Model 1"

    """
    ==================================
    Test validation methods
    ==================================
    """
    def test_validate_image_method_with_content_type(self):
        """Test validate_image method with content_type provided"""
        simple_model = SimpleModelWithImageable(
            name="Test Model",
            images=[
                Images(
                    file="test image 1",
                    content_type="simple_model_with_imageable"
                ),
                Images(
                    file="test image 2",
                    content_type="simple_model_with_imageable"
                )
            ]
        )
        assert simple_model.images[0].content_type == "simple_model_with_imageable"
        assert simple_model.images[1].content_type == "simple_model_with_imageable"

    def test_validate_image_method_without_content_type(self):
        """Test validate_image method without content_type provided"""
        simple_model = SimpleModelWithImageable(
            name="Test Model",
            images=[Images(file="test image 1"), Images(file="test image 2")]
        )
        assert simple_model.images[0].content_type == "simple_model_with_imageable"
        assert simple_model.images[1].content_type == "simple_model_with_imageable"

    def test_validate_image_method_with_and_without_content_type(self):
        """Test validate_image method with empty content_type provided"""
        simple_model = SimpleModelWithImageable(
            name="Test Model",
            images=[
                Images(file="test image 1"),
                Images(
                    file="test image 2",
                    content_type="simple_model_with_imageable"
                )
            ]
        )
        assert simple_model.images[0].content_type == "simple_model_with_imageable"
        assert simple_model.images[1].content_type == "simple_model_with_imageable"

    def test_validate_image_method_with_blank_content_type(self):
        """Test validate_image method with blank content_type provided"""
        simple_model = SimpleModelWithImageable(
            name="Test Model",
            images=[Images(file="test image 1", content_type="  ")]
        )
        assert simple_model.images[0].content_type == "simple_model_with_imageable"

    def test_validate_image_method_with_content_type_is_none(self):
        simple_model = SimpleModelWithImageable(
            name="Test Model",
            images=[Images(file="test image 1", content_type=None)]
        )
        assert simple_model.images[0].content_type == "simple_model_with_imageable"

    @pytest.mark.asyncio
    async def test_validate_image_method_with_other_falsy_values(
        self, db_session: AsyncSession
    ):
        simple_model = SimpleModelWithImageable(
            name="Test Model",
            images=[Images(file="test image 1", content_type=0)]
        )
        with pytest.raises(DBAPIError):
            await save_object(db_session, simple_model)
        await db_session.rollback()

        simple_model = SimpleModelWithImageable(
            name="Test Model",
            images=[Images(file="test image 1", content_type=False)]
        )
        with pytest.raises(DBAPIError):
            await save_object(db_session, simple_model)
        await db_session.rollback()
