from typing import Optional, Literal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import StrictStr
from pydantic_core import PydanticUndefined
import pytest

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema, StrictPositiveInt
)
from app.schemas.sku_schema import (
    SkuBase, SkuCreate,
    SkuUpdate, SkuInDB,
    SkuResponse, SkuPathItem
)
from app.schemas.category_schema import CategoryPathItem
from app.schemas.product_schema import ProductPathItem
from app.models.sku_model import Skus
from app.models.product_model import Products
from app.models.category_model import Categories
from app.models.category_type_model import CategoryTypes
from app.models.supplier_model import Suppliers
from tests.utils.model_test_utils import save_object


class TestSkuBase:
    """Test cases for the SKU base schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.sku_dict = {
            "name": "Test SKU",
            "description": "Test SKU Description",
            "product_id": 1
        }

    def test_sku_base_schema_inheritance(self):
        """Test that the SKU base schema inherits from BaseSchema"""
        assert issubclass(SkuBase, BaseSchema)

    def test_sku_base_fields_inheritance(self):
        """Test that the SKU base schema has correct fields"""
        fields = SkuBase.model_fields
        assert len(fields) == 3
        assert 'name' in fields
        assert 'description' in fields
        assert 'product_id' in fields

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

        product_id = fields['product_id']
        assert product_id.is_required() is True
        assert product_id.annotation == int
        assert product_id.default is PydanticUndefined
        assert product_id.metadata[0].strict is True
        assert product_id.metadata[1].gt == 0

    def test_sku_base_schema_input(self):
        schema = SkuBase(**self.sku_dict)
        assert schema.name == "Test SKU"
        assert schema.description == "Test SKU Description"
        assert schema.product_id == 1

    def test_sku_base_schema_input_updated(self):
        schema = SkuBase(**self.sku_dict)
        assert schema.name == "Test SKU"
        assert schema.description == "Test SKU Description"
        assert schema.product_id == 1

        schema.name = "Test SKU Updated"
        assert schema.name == "Test SKU Updated"

    def test_sku_base_schema_model_dump(self):
        schema = SkuBase(**self.sku_dict)
        assert schema.model_dump() == {
            "name": "Test SKU",
            "description": "Test SKU Description",
            "product_id": 1
        }

    def test_sku_base_schema_model_dump_json(self):
        schema = SkuBase(**self.sku_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"Test SKU",'\
            '"description":"Test SKU Description",'\
            '"product_id":1'\
            '}'


class TestSkuCreate:
    """Test cases for the SKU create schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.sku_dict = {
            "name": "Test SKU",
            "description": "Test SKU Description",
            "product_id": 1
        }

    def test_sku_create_schema_inheritance(self):
        """Test that the SKU create schema inherits from BaseCreateSchema"""
        assert issubclass(SkuCreate, BaseCreateSchema)
        assert issubclass(SkuCreate, SkuBase)

    def test_sku_create_fields_inheritance(self):
        """Test that the SKU create schema has correct fields"""
        fields = SkuCreate.model_fields
        assert len(fields) == 5
        assert 'name' in fields
        assert 'description' in fields
        assert 'product_id' in fields

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

        product_id = fields['product_id']
        assert product_id.is_required() is True
        assert product_id.annotation == int
        assert product_id.default is PydanticUndefined
        assert product_id.metadata[0].strict is True
        assert product_id.metadata[1].gt == 0

    def test_sku_create_schema_input(self):
        schema = SkuCreate(**self.sku_dict)
        assert schema.name == "Test SKU"
        assert schema.description == "Test SKU Description"
        assert schema.product_id == 1

    def test_sku_create_schema_input_updated(self):
        schema = SkuCreate(**self.sku_dict)
        assert schema.name == "Test SKU"
        assert schema.description == "Test SKU Description"
        assert schema.product_id == 1

        schema.name = "Test SKU Updated"
        assert schema.name == "Test SKU Updated"

    def test_sku_create_schema_model_dump(self):
        schema = SkuCreate(**self.sku_dict)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "name": "Test SKU",
            "description": "Test SKU Description",
            "product_id": 1
        }

    def test_sku_create_schema_model_dump_json(self):
        schema = SkuCreate(**self.sku_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"name":"Test SKU",'\
            '"description":"Test SKU Description",'\
            '"product_id":1'\
            '}'


class TestSkuUpdate:
    """Test cases for the SKU update schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.sku_dict = {
            "name": "Test SKU",
            "description": "Test SKU Description",
            "product_id": 1
        }

    def test_sku_update_schema_inheritance(self):
        """Test that the SKU update schema inherits from BaseUpdateSchema"""
        assert issubclass(SkuUpdate, BaseUpdateSchema)
        assert issubclass(SkuUpdate, SkuBase)

    def test_sku_update_fields_inheritance(self):
        """Test that the SKU update schema has correct fields"""
        fields = SkuUpdate.model_fields
        assert len(fields) == 5
        assert 'name' in fields
        assert 'description' in fields
        assert 'product_id' in fields

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

        product_id = fields['product_id']
        assert product_id.is_required() is False
        assert product_id.annotation == Optional[StrictPositiveInt]
        assert product_id.default is None

    def test_sku_update_schema_input(self):
        schema = SkuUpdate(**self.sku_dict)
        assert schema.name == "Test SKU"
        assert schema.description == "Test SKU Description"
        assert schema.product_id == 1

    def test_sku_update_schema_input_updated(self):
        schema = SkuUpdate(**self.sku_dict)
        assert schema.name == "Test SKU"
        assert schema.description == "Test SKU Description"
        assert schema.product_id == 1

        schema.name = "Test SKU Updated"
        assert schema.name == "Test SKU Updated"

    def test_sku_update_schema_model_dump(self):
        schema = SkuUpdate(**self.sku_dict)
        assert schema.model_dump() == {
            "is_active": None,
            "sequence": None,
            "name": "Test SKU",
            "description": "Test SKU Description",
            "product_id": 1
        }

    def test_sku_update_schema_model_dump_json(self):
        schema = SkuUpdate(**self.sku_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":null,'\
            '"sequence":null,'\
            '"name":"Test SKU",'\
            '"description":"Test SKU Description",'\
            '"product_id":1'\
            '}'


class TestSkuPathItem:
    """Test cases for the SKU path item schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.sku_path_item_dict = {
            "name": "Test SKU",
            "slug": "test-sku",
            "sku_number": "A1B2C3D4E5",
            "type": "SKU"
        }

    def test_sku_path_item_schema_inheritance(self):
        """Test that the SKU path item schema inherits from BaseSchema"""
        assert issubclass(SkuPathItem, BaseSchema)

    def test_sku_path_item_fields_inheritance(self):
        """Test that the SKU path item schema has correct fields"""
        fields = SkuPathItem.model_fields
        assert len(fields) == 4
        assert 'name' in fields
        assert 'slug' in fields
        assert 'sku_number' in fields
        assert 'type' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        sku_number = fields['sku_number']
        assert sku_number.is_required() is True
        assert sku_number.annotation == str
        assert sku_number.default is PydanticUndefined

        type = fields['type']
        assert type.is_required() is False
        assert type.annotation == Literal["SKU"]
        assert type.default == "SKU"

    def test_sku_path_item_schema_input(self):
        schema = SkuPathItem(**self.sku_path_item_dict)
        assert schema.name == "Test SKU"
        assert schema.slug == "test-sku"
        assert schema.sku_number == "A1B2C3D4E5"
        assert schema.type == "SKU"

    def test_sku_path_item_schema_input_updated(self):
        schema = SkuPathItem(**self.sku_path_item_dict)
        assert schema.name == "Test SKU"
        assert schema.slug == "test-sku"
        assert schema.sku_number == "A1B2C3D4E5"
        assert schema.type == "SKU"

        schema.name = "Test SKU Updated"
        assert schema.name == "Test SKU Updated"

    def test_sku_path_item_schema_model_dump(self):
        schema = SkuPathItem(**self.sku_path_item_dict)
        assert schema.model_dump() == {
            "name": "Test SKU",
            "slug": "test-sku",
            "sku_number": "A1B2C3D4E5",
            "type": "SKU"
        }

    def test_sku_path_item_schema_model_dump_json(self):
        schema = SkuPathItem(**self.sku_path_item_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"Test SKU",'\
            '"slug":"test-sku",'\
            '"sku_number":"A1B2C3D4E5",'\
            '"type":"SKU"'\
            '}'


class TestSkuInDB:
    """Test cases for the SKU in db schema"""

    def test_sku_in_db_inheritance(self):
        """Test that the SKU in db schema inherits from BaseInDB"""
        assert issubclass(SkuInDB, BaseInDB)
        assert issubclass(SkuInDB, SkuBase)

    def test_sku_in_db_fields_inheritance(self):
        """Test that the SKU in db schema has correct fields"""
        fields = SkuInDB.model_fields
        assert len(fields) == 12
        assert 'name' in fields
        assert 'description' in fields
        assert 'product_id' in fields
        assert 'slug' in fields
        assert 'sku_number' in fields

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

        product_id = fields['product_id']
        assert product_id.is_required() is True
        assert product_id.annotation == int
        assert product_id.default is PydanticUndefined

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        sku_number = fields['sku_number']
        assert sku_number.is_required() is True
        assert sku_number.annotation == str
        assert sku_number.default is PydanticUndefined

        model_config = SkuInDB.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_sku_in_db_model_validate(self, db_session: AsyncSession):
        """Test that the SKU in db schema model validate"""
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        category = Categories(name="Test Category", category_type_id=category_type.id)
        await save_object(db_session, category)

        supplier = Suppliers(
            name="Test Supplier",
            company_type="PT",
            address="Test Address",
            contact="081234567890",
            email="test@supplier.com"
        )
        await save_object(db_session, supplier)

        product = Products(
            name="Test Product",
            description="Test Product Description",
            category_id=category.id,
            supplier_id=supplier.id
        )
        await save_object(db_session, product)

        model = Skus(
            name="Test SKU",
            description="Test SKU Description",
            product_id=product.id
        )
        await save_object(db_session, model)

        query = select(Skus).where(Skus.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = SkuInDB.model_validate(db_model)
        assert db_schema_object == SkuInDB(
            id=model.id,
            name="Test SKU",
            description="Test SKU Description",
            slug="test-sku",
            sku_number=model.sku_number,
            product_id=product.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )

    @pytest.mark.asyncio
    async def test_sku_in_db_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the SKU in db schema model validate updated"""
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        category = Categories(name="Test Category", category_type_id=category_type.id)
        await save_object(db_session, category)

        supplier = Suppliers(
            name="Test Supplier",
            company_type="PT",
            address="Test Address",
            contact="081234567890",
            email="test@supplier.com"
        )
        await save_object(db_session, supplier)

        product = Products(
            name="Test Product",
            description="Test Product Description",
            category_id=category.id,
            supplier_id=supplier.id
        )
        await save_object(db_session, product)

        model = Skus(
            name="Test SKU",
            description="Test SKU Description",
            product_id=product.id
        )
        await save_object(db_session, model)

        query = select(Skus).where(Skus.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Test SKU Updated"
        db_model.description = "Test SKU Description Updated"

        db_schema_object = SkuInDB.model_validate(db_model)
        assert db_schema_object == SkuInDB(
            id=model.id,
            name="Test SKU Updated",
            description="Test SKU Description Updated",
            slug="test-sku-updated",
            sku_number=model.sku_number,
            product_id=product.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )


class TestSkuResponse:
    """Test cases for the SKU response schema"""

    def test_sku_response_inheritance(self):
        """Test that the SKU response schema inherits from SkuInDB"""
        assert issubclass(SkuResponse, SkuInDB)

    def test_sku_response_fields_inheritance(self):
        """Test that the SKU response schema has correct fields"""
        fields = SkuResponse.model_fields
        assert len(fields) == 13
        assert 'name' in fields
        assert 'description' in fields
        assert 'product_id' in fields
        assert 'slug' in fields
        assert 'sku_number' in fields
        assert 'full_path' in fields

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

        product_id = fields['product_id']
        assert product_id.is_required() is True
        assert product_id.annotation == int
        assert product_id.default is PydanticUndefined

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        sku_number = fields['sku_number']
        assert sku_number.is_required() is True
        assert sku_number.annotation == str
        assert sku_number.default is PydanticUndefined

        full_path = fields['full_path']
        assert full_path.is_required() is True
        # Check that it's a List with Annotated Union - exact comparison is complex
        annotation_str = str(full_path.annotation)
        assert annotation_str.startswith('typing.List[typing.Annotated[typing.Union[')
        assert 'discriminator' in str(full_path.annotation)
        assert full_path.default is PydanticUndefined

        model_config = SkuResponse.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_sku_response_model_validate(self, db_session: AsyncSession):
        """Test that the SKU response schema model validate"""
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        parent_category = Categories(
            name="Parent Category",
            category_type_id=category_type.id
        )
        await save_object(db_session, parent_category)

        child_category = Categories(
            name="Child Category",
            parent_id=parent_category.id
        )
        await save_object(db_session, child_category)

        supplier = Suppliers(
            name="Test Supplier",
            company_type="PT",
            address="Test Address",
            contact="081234567890",
            email="test@supplier.com"
        )
        await save_object(db_session, supplier)

        product = Products(
            name="Test Product",
            description="Test Product Description",
            category_id=child_category.id,
            supplier_id=supplier.id
        )
        await save_object(db_session, product)

        model = Skus(
            name="Test SKU",
            description="Test SKU Description",
            product_id=product.id
        )
        await save_object(db_session, model)

        query = select(Skus).where(Skus.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = SkuResponse.model_validate(db_model)

        assert db_schema_object == SkuResponse(
            id=model.id,
            name="Test SKU",
            description="Test SKU Description",
            slug="test-sku",
            sku_number=model.sku_number,
            product_id=product.id,
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
                ),
                ProductPathItem(
                    name="Test Product",
                    slug="test-product",
                    type="Product"
                ),
                SkuPathItem(
                    name="Test SKU",
                    slug="test-sku",
                    sku_number=model.sku_number,
                    type="SKU"
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
    async def test_sku_response_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the SKU response schema model validate updated"""
        category_type = CategoryTypes(name="Test Category Type")
        await save_object(db_session, category_type)

        parent_category = Categories(
            name="Parent Category",
            category_type_id=category_type.id
        )
        await save_object(db_session, parent_category)

        child_category = Categories(
            name="Child Category",
            parent_id=parent_category.id
        )
        await save_object(db_session, child_category)

        supplier = Suppliers(
            name="Test Supplier",
            company_type="PT",
            address="Test Address",
            contact="081234567890",
            email="test@supplier.com"
        )
        await save_object(db_session, supplier)

        product = Products(
            name="Test Product",
            description="Test Product Description",
            category_id=child_category.id,
            supplier_id=supplier.id
        )
        await save_object(db_session, product)

        model = Skus(
            name="Test SKU",
            description="Test SKU Description",
            product_id=product.id
        )
        await save_object(db_session, model)

        query = select(Skus).where(Skus.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.full_path[0]['name'] = "Full Path Parent Category Updated"
        db_model.full_path[1]['name'] = "Full Path Child Category Updated"
        db_model.full_path[2]['name'] = "Full Path Product Updated"
        db_model.full_path[3]['name'] = "Full Path SKU Updated"

        # Full path is just a property. Even if we update the full path, when model
        # validate is called, the full path will be recomputed and got normal value

        db_schema_object = SkuResponse.model_validate(db_model)
        assert db_schema_object == SkuResponse(
            id=model.id,
            name="Test SKU",
            description="Test SKU Description",
            slug="test-sku",
            sku_number=model.sku_number,
            product_id=product.id,
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
                ),
                ProductPathItem(
                    name="Test Product",
                    slug="test-product",
                    type="Product"
                ),
                SkuPathItem(
                    name="Test SKU",
                    slug="test-sku",
                    sku_number=model.sku_number,
                    type="SKU"
                )
            ],
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )
