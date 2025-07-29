from typing import Optional, List

from sqlalchemy import Column, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import Field
import pytest

from app.core.base import Base
from app.schemas.image_schema import ImageCreate, ImageUpdate, ImageSummary
from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema, StrictPositiveInt
)
from app.utils.mixins import Imageable
from tests.utils.model_test_utils import save_object
from app.models.image_model import Images


class SampleModelBase3(Base, Imageable):
    """Sample model for Base functionality testing."""
    name = Column(String, nullable=False)


class SampleSchemaBase(BaseSchema):
    """Sample schema for base testing"""
    name: str


class SampleSchemaCreate(SampleSchemaBase, BaseCreateSchema):
    """Sample schema for creating a new sample"""
    images: List[ImageCreate] = Field(default_factory=list)


class SampleSchemaUpdate(SampleSchemaBase, BaseUpdateSchema):
    """Schema for updating an existing sample"""
    name: Optional[str] = None
    images_to_create: Optional[List[ImageCreate]] = None
    images_to_update: Optional[List[ImageUpdate]] = None
    images_to_delete: Optional[List[StrictPositiveInt]] = None


class SampleSchemaInDB(SampleSchemaBase, BaseInDB):
    """Schema for Sample as stored in database"""
    pass


class SampleSchemaResponse(SampleSchemaInDB):
    """Schema for Sample API responses"""
    images: List[ImageSummary] = None


class TestSampleSchemaCreate:
    """Test cases for the SampleSchemaCreate schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.sample_dict = {
            "name": "Test Sample",
            "images": [
                {
                    "file": "test-image-1.jpg",
                    "title": "Test Image 1",
                    "is_primary": True
                },
                {
                    "file": "test-image-2.jpg",
                    "title": "Test Image 2",
                    "is_primary": False
                }
            ]
        }

    def test_sample_schema_create_fields_inheritance(self):
        """Test that the SampleSchemaCreate schema has correct fields"""
        fields = SampleSchemaCreate.model_fields
        assert len(fields) == 4
        assert 'name' in fields
        assert 'images' in fields

        images = fields['images']
        assert images.is_required() is False
        assert images.annotation == List[ImageCreate]
        assert images.default_factory == list

    def test_sample_schema_create_schema_input(self):
        """Test that the SampleSchemaCreate schema has correct input"""
        schema = SampleSchemaCreate(**self.sample_dict)
        assert schema.name == "Test Sample"
        assert schema.images == [
            ImageCreate(file="test-image-1.jpg", title="Test Image 1", is_primary=True),
            ImageCreate(file="test-image-2.jpg", title="Test Image 2", is_primary=False)
        ]

    def test_sample_schema_create_schema_input_updated(self):
        """Test that the SampleSchemaCreate schema has correct input"""
        schema = SampleSchemaCreate(**self.sample_dict)
        assert schema.name == "Test Sample"
        assert schema.images == [
            ImageCreate(file="test-image-1.jpg", title="Test Image 1", is_primary=True),
            ImageCreate(file="test-image-2.jpg", title="Test Image 2", is_primary=False)
        ]

        schema.images = "test-sample-image.jpg"
        assert schema.images == "test-sample-image.jpg"

    def test_sample_schema_create_schema_model_dump(self):
        schema = SampleSchemaCreate(**self.sample_dict)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "name": "Test Sample",
            "images": [
                {
                    "file": "test-image-1.jpg",
                    "title": "Test Image 1",
                    "is_primary": True
                },
                {
                    "file": "test-image-2.jpg",
                    "title": "Test Image 2",
                    "is_primary": False
                }
            ]
        }

    def test_sample_schema_create_schema_model_dump_json(self):
        schema = SampleSchemaCreate(**self.sample_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"name":"Test Sample",'\
            '"images":['\
            '{"file":"test-image-1.jpg",'\
            '"title":"Test Image 1",'\
            '"is_primary":true},'\
            '{"file":"test-image-2.jpg",'\
            '"title":"Test Image 2",'\
            '"is_primary":false}'\
            ']'\
            '}'


class TestSampleSchemaUpdate:
    """Test cases for the SampleSchemaUpdate schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.sample_dict = {
            "name": "Test Sample",
            "images_to_create": [
                {
                    "file": "test-image-1.jpg",
                    "title": "Test Image 1",
                    "is_primary": True
                }
            ],
            "images_to_update": [
                {
                    "id": 1,
                    "file": "test-image-1.jpg",
                    "title": "Test Image 1 Updated",
                    "is_primary": False
                }
            ],
            "images_to_delete": [2]
        }

    def test_sample_schema_update_fields_inheritance(self):
        """Test that the SampleSchemaUpdate schema has correct fields"""
        fields = SampleSchemaUpdate.model_fields
        assert len(fields) == 6
        assert 'name' in fields
        assert 'images_to_create' in fields
        assert 'images_to_update' in fields
        assert 'images_to_delete' in fields

        images_to_create = fields['images_to_create']
        assert images_to_create.is_required() is False
        assert images_to_create.annotation == Optional[List[ImageCreate]]
        assert images_to_create.default is None

        images_to_update = fields['images_to_update']
        assert images_to_update.is_required() is False
        assert images_to_update.annotation == Optional[List[ImageUpdate]]
        assert images_to_update.default is None

        images_to_delete = fields['images_to_delete']
        assert images_to_delete.is_required() is False
        assert images_to_delete.annotation == Optional[List[StrictPositiveInt]]
        assert images_to_delete.default is None

    def test_sample_schema_update_schema_input(self):
        """Test that the SampleSchemaUpdate schema has correct input"""
        schema = SampleSchemaUpdate(**self.sample_dict)
        assert schema.name == "Test Sample"
        assert schema.images_to_create == [
            ImageCreate(file="test-image-1.jpg", title="Test Image 1", is_primary=True)
        ]
        assert schema.images_to_update == [
            ImageUpdate(
                id=1,
                file="test-image-1.jpg",
                title="Test Image 1 Updated",
                is_primary=False
            )
        ]
        assert schema.images_to_delete == [2]

    def test_sample_schema_update_schema_input_updated(self):
        """Test that the SampleSchemaUpdate schema has correct input"""
        schema = SampleSchemaUpdate(**self.sample_dict)
        assert schema.name == "Test Sample"
        assert schema.images_to_create == [
            ImageCreate(file="test-image-1.jpg", title="Test Image 1", is_primary=True)
        ]
        assert schema.images_to_update == [
            ImageUpdate(
                id=1,
                file="test-image-1.jpg",
                title="Test Image 1 Updated",
                is_primary=False
            )
        ]
        assert schema.images_to_delete == [2]

        schema.images_to_create = "test-image-2.jpg"
        assert schema.images_to_create == "test-image-2.jpg"

        schema.images_to_update = "test-image-3.jpg"
        assert schema.images_to_update == "test-image-3.jpg"

        schema.images_to_delete = "test-image-4.jpg"
        assert schema.images_to_delete == "test-image-4.jpg"

    def test_sample_schema_update_schema_model_dump(self):
        schema = SampleSchemaUpdate(**self.sample_dict)
        assert schema.model_dump() == {
            "is_active": None,
            "sequence": None,
            "name": "Test Sample",
            "images_to_create": [
                {
                    "file": "test-image-1.jpg",
                    "title": "Test Image 1",
                    "is_primary": True
                }
            ],
            "images_to_update": [
                {
                    "id": 1,
                    "file": "test-image-1.jpg",
                    "title": "Test Image 1 Updated",
                    "is_primary": False
                }
            ],
            "images_to_delete": [2]
        }

    def test_sample_schema_update_schema_model_dump_json(self):
        schema = SampleSchemaUpdate(**self.sample_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":null,'\
            '"sequence":null,'\
            '"name":"Test Sample",'\
            '"images_to_create":['\
            '{"file":"test-image-1.jpg",'\
            '"title":"Test Image 1",'\
            '"is_primary":true}'\
            '],'\
            '"images_to_update":['\
            '{"id":1,'\
            '"file":"test-image-1.jpg",'\
            '"title":"Test Image 1 Updated",'\
            '"is_primary":false}'\
            '],'\
            '"images_to_delete":[2]'\
            '}'


class TestSampleSchemaResponse:
    """Test cases for the SampleSchemaResponse schema"""

    def test_sample_schema_response_fields_inheritance(self):
        """Test that the SampleSchemaResponse schema has correct fields"""
        fields = SampleSchemaResponse.model_fields
        assert len(fields) == 9
        assert 'images' in fields

        images = fields['images']
        assert images.is_required() is False
        assert images.annotation == List[ImageSummary]
        assert images.default is None

    @pytest.mark.asyncio
    async def test_sample_schema_response_model_validate(
        self, db_session: AsyncSession
    ):
        """Test that the SampleSchemaResponse schema has correct input"""
        model = SampleModelBase3(
            name="Test Sample",
            images=[
                Images(
                    file="test-image-1.jpg",
                    title="Test Image 1",
                    is_primary=True
                ),
                Images(
                    file="test-image-2.jpg",
                    title="Test Image 2",
                    is_primary=False
                )
            ]
        )
        await save_object(db_session, model)

        query = select(SampleModelBase3).where(SampleModelBase3.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()
        await db_session.refresh(db_model, ['images'])

        db_schema_object = SampleSchemaResponse.model_validate(db_model)

        assert db_schema_object == SampleSchemaResponse(
            id=model.id,
            name="Test Sample",
            images=[
                ImageSummary(
                    id=1,
                    file="test-image-1.jpg",
                    title="Test Image 1",
                    is_primary=True
                ),
                ImageSummary(
                    id=2,
                    file="test-image-2.jpg",
                    title="Test Image 2",
                    is_primary=False
                )
            ],
            is_active=True,
            sequence=0,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        )

    @pytest.mark.asyncio
    async def test_sample_schema_response_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the SampleSchemaResponse schema model validate updated"""
        model = SampleModelBase3(
            name="Test Sample",
            images=[
                Images(
                    file="test-image-1.jpg",
                    title="Test Image 1",
                    is_primary=True
                ),
                Images(
                    file="test-image-2.jpg",
                    title="Test Image 2",
                    is_primary=False
                )
            ]
        )
        await save_object(db_session, model)

        query = select(SampleModelBase3).where(SampleModelBase3.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()
        await db_session.refresh(db_model, ['images'])

        db_schema_object = SampleSchemaResponse.model_validate(db_model)

        assert db_schema_object == SampleSchemaResponse(
            id=model.id,
            name="Test Sample",
            images=[
                ImageSummary(
                    id=1,
                    file="test-image-1.jpg",
                    title="Test Image 1",
                    is_primary=True
                ),
                ImageSummary(
                    id=2,
                    file="test-image-2.jpg",
                    title="Test Image 2",
                    is_primary=False
                )
            ],
            is_active=True,
            sequence=0,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        )
