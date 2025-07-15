from sqlalchemy import String, event, Text, Integer, CheckConstraint, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
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
async def setup_images(image_factory):
    """
    Fixture to create images ONCE for the entire test module.
    This is the efficient part.
    """
    image1 = await image_factory(
        file="test_folder/test1.jpg"
    )
    image2 = await image_factory(
        file="test_folder/test2.jpg",
        title="Test Image 2",
        is_primary=True
    )
    return image1, image2


class TestImage:
    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_images):
        self.test_image1, self.test_image2 = setup_images

    def test_inheritance_from_base_model(self):
        assert issubclass(Images, Base)
