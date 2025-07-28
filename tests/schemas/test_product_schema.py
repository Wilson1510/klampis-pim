from typing import Optional, Literal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import StrictStr
from pydantic_core import PydanticUndefined
import pytest

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema, StrictPositiveInt
)
from app.schemas.product_schema import (
    ProductBase, ProductCreate,
    ProductUpdate, ProductInDB,
    ProductResponse, ProductPathItem
)
from app.schemas.category_schema import CategoryPathItem
from app.models.product_model import Products
from app.models.category_model import Categories
from app.models.category_type_model import CategoryTypes
from app.models.supplier_model import Suppliers
from tests.utils.model_test_utils import save_object


class TestProductBase:
    """Test cases for the product base schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.product_dict = {
            "name": "Test Product",
            "description": "Test Product Description",
            "category_id": 1,
            "supplier_id": 1
        }

    def test_product_base_schema_inheritance(self):
        """Test that the product base schema inherits from BaseSchema"""
        assert issubclass(ProductBase, BaseSchema)

    def test_product_base_fields_inheritance(self):
        """Test that the product base schema has correct fields"""
        fields = ProductBase.model_fields
        assert len(fields) == 4
        assert 'name' in fields
        assert 'description' in fields
        assert 'category_id' in fields
        assert 'supplier_id' in fields

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

        category_id = fields['category_id']
        assert category_id.is_required() is True
        assert category_id.annotation == int
        assert category_id.default is PydanticUndefined
        assert category_id.metadata[0].strict is True
        assert category_id.metadata[1].gt == 0

        supplier_id = fields['supplier_id']
        assert supplier_id.is_required() is True
        assert supplier_id.annotation == int
        assert supplier_id.default is PydanticUndefined
        assert supplier_id.metadata[0].strict is True
        assert supplier_id.metadata[1].gt == 0

    def test_product_base_schema_input(self):
        schema = ProductBase(**self.product_dict)
        assert schema.name == "Test Product"
        assert schema.description == "Test Product Description"
        assert schema.category_id == 1
        assert schema.supplier_id == 1

    def test_product_base_schema_input_updated(self):
        schema = ProductBase(**self.product_dict)
        assert schema.name == "Test Product"
        assert schema.description == "Test Product Description"
        assert schema.category_id == 1
        assert schema.supplier_id == 1

        schema.name = "Test Product Updated"
        assert schema.name == "Test Product Updated"

    def test_product_base_schema_model_dump(self):
        schema = ProductBase(**self.product_dict)
        assert schema.model_dump() == {
            "name": "Test Product",
            "description": "Test Product Description",
            "category_id": 1,
            "supplier_id": 1
        }

    def test_product_base_schema_model_dump_json(self):
        schema = ProductBase(**self.product_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"Test Product",'\
            '"description":"Test Product Description",'\
            '"category_id":1,'\
            '"supplier_id":1'\
            '}'


class TestProductCreate:
    """Test cases for the product create schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.product_dict = {
            "name": "Test Product",
            "description": "Test Product Description",
            "category_id": 1,
            "supplier_id": 1
        }

    def test_product_create_schema_inheritance(self):
        """Test that the product create schema inherits from BaseCreateSchema"""
        assert issubclass(ProductCreate, BaseCreateSchema)
        assert issubclass(ProductCreate, ProductBase)

    def test_product_create_fields_inheritance(self):
        """Test that the product create schema has correct fields"""
        fields = ProductCreate.model_fields
        assert len(fields) == 6
        assert 'name' in fields
        assert 'description' in fields
        assert 'category_id' in fields
        assert 'supplier_id' in fields

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

        category_id = fields['category_id']
        assert category_id.is_required() is True
        assert category_id.annotation == int
        assert category_id.default is PydanticUndefined
        assert category_id.metadata[0].strict is True
        assert category_id.metadata[1].gt == 0

        supplier_id = fields['supplier_id']
        assert supplier_id.is_required() is True
        assert supplier_id.annotation == int
        assert supplier_id.default is PydanticUndefined
        assert supplier_id.metadata[0].strict is True
        assert supplier_id.metadata[1].gt == 0

    def test_product_create_schema_input(self):
        schema = ProductCreate(**self.product_dict)
        assert schema.name == "Test Product"
        assert schema.description == "Test Product Description"
        assert schema.category_id == 1
        assert schema.supplier_id == 1

    def test_product_create_schema_input_updated(self):
        schema = ProductCreate(**self.product_dict)
        assert schema.name == "Test Product"
        assert schema.description == "Test Product Description"
        assert schema.category_id == 1
        assert schema.supplier_id == 1

        schema.name = "Test Product Updated"
        assert schema.name == "Test Product Updated"

    def test_product_create_schema_model_dump(self):
        schema = ProductCreate(**self.product_dict)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "name": "Test Product",
            "description": "Test Product Description",
            "category_id": 1,
            "supplier_id": 1
        }

    def test_product_create_schema_model_dump_json(self):
        schema = ProductCreate(**self.product_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"name":"Test Product",'\
            '"description":"Test Product Description",'\
            '"category_id":1,'\
            '"supplier_id":1'\
            '}'


class TestProductUpdate:
    """Test cases for the product update schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.product_dict = {
            "name": "Test Product",
            "description": "Test Product Description",
            "category_id": 1,
            "supplier_id": 1
        }

    def test_product_update_schema_inheritance(self):
        """Test that the product update schema inherits from BaseUpdateSchema"""
        assert issubclass(ProductUpdate, BaseUpdateSchema)
        assert issubclass(ProductUpdate, ProductBase)

    def test_product_update_fields_inheritance(self):
        """Test that the product update schema has correct fields"""
        fields = ProductUpdate.model_fields
        assert len(fields) == 6
        assert 'name' in fields
        assert 'description' in fields
        assert 'category_id' in fields
        assert 'supplier_id' in fields

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

        category_id = fields['category_id']
        assert category_id.is_required() is False
        assert category_id.annotation == Optional[StrictPositiveInt]
        assert category_id.default is None

        supplier_id = fields['supplier_id']
        assert supplier_id.is_required() is False
        assert supplier_id.annotation == Optional[StrictPositiveInt]
        assert supplier_id.default is None

    def test_product_update_schema_input(self):
        schema = ProductUpdate(**self.product_dict)
        assert schema.name == "Test Product"
        assert schema.description == "Test Product Description"
        assert schema.category_id == 1
        assert schema.supplier_id == 1

    def test_product_update_schema_input_updated(self):
        schema = ProductUpdate(**self.product_dict)
        assert schema.name == "Test Product"
        assert schema.description == "Test Product Description"
        assert schema.category_id == 1
        assert schema.supplier_id == 1

        schema.name = "Test Product Updated"
        assert schema.name == "Test Product Updated"

    def test_product_update_schema_model_dump(self):
        schema = ProductUpdate(**self.product_dict)
        assert schema.model_dump() == {
            "is_active": None,
            "sequence": None,
            "name": "Test Product",
            "description": "Test Product Description",
            "category_id": 1,
            "supplier_id": 1
        }

    def test_product_update_schema_model_dump_json(self):
        schema = ProductUpdate(**self.product_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":null,'\
            '"sequence":null,'\
            '"name":"Test Product",'\
            '"description":"Test Product Description",'\
            '"category_id":1,'\
            '"supplier_id":1'\
            '}'


class TestProductPathItem:
    """Test cases for the product path item schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.product_path_item_dict = {
            "name": "Test Product",
            "slug": "test-product",
            "type": "Product"
        }

    def test_product_path_item_schema_inheritance(self):
        """Test that the product path item schema inherits from BaseSchema"""
        assert issubclass(ProductPathItem, BaseSchema)

    def test_product_path_item_fields_inheritance(self):
        """Test that the product path item schema has correct fields"""
        fields = ProductPathItem.model_fields
        assert len(fields) == 3
        assert 'name' in fields
        assert 'slug' in fields
        assert 'type' in fields

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        type = fields['type']
        assert type.is_required() is False
        assert type.annotation == Literal["Product"]
        assert type.default == "Product"

    def test_product_path_item_schema_input(self):
        schema = ProductPathItem(**self.product_path_item_dict)
        assert schema.name == "Test Product"
        assert schema.slug == "test-product"
        assert schema.type == "Product"

    def test_product_path_item_schema_input_updated(self):
        schema = ProductPathItem(**self.product_path_item_dict)
        assert schema.name == "Test Product"
        assert schema.slug == "test-product"
        assert schema.type == "Product"

        schema.name = "Test Product Updated"
        assert schema.name == "Test Product Updated"

    def test_product_path_item_schema_model_dump(self):
        schema = ProductPathItem(**self.product_path_item_dict)
        assert schema.model_dump() == {
            "name": "Test Product",
            "slug": "test-product",
            "type": "Product"
        }

    def test_product_path_item_schema_model_dump_json(self):
        schema = ProductPathItem(**self.product_path_item_dict)
        assert schema.model_dump_json() == '{'\
            '"name":"Test Product",'\
            '"slug":"test-product",'\
            '"type":"Product"'\
            '}'


class TestProductInDB:
    """Test cases for the product in db schema"""

    def test_product_in_db_inheritance(self):
        """Test that the product in db schema inherits from BaseInDB"""
        assert issubclass(ProductInDB, BaseInDB)
        assert issubclass(ProductInDB, ProductBase)

    def test_product_in_db_fields_inheritance(self):
        """Test that the product in db schema has correct fields"""
        fields = ProductInDB.model_fields
        assert len(fields) == 12
        assert 'name' in fields
        assert 'description' in fields
        assert 'category_id' in fields
        assert 'supplier_id' in fields
        assert 'slug' in fields

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

        category_id = fields['category_id']
        assert category_id.is_required() is True
        assert category_id.annotation == int
        assert category_id.default is PydanticUndefined

        supplier_id = fields['supplier_id']
        assert supplier_id.is_required() is True
        assert supplier_id.annotation == int
        assert supplier_id.default is PydanticUndefined

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        model_config = ProductInDB.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_product_in_db_model_validate(self, db_session: AsyncSession):
        """Test that the product in db schema model validate"""
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

        model = Products(
            name="Test Product",
            description="Test Product Description",
            category_id=category.id,
            supplier_id=supplier.id
        )
        await save_object(db_session, model)

        query = select(Products).where(Products.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = ProductInDB.model_validate(db_model)
        assert db_schema_object == ProductInDB(
            id=model.id,
            name="Test Product",
            description="Test Product Description",
            slug="test-product",
            category_id=category.id,
            supplier_id=supplier.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )

    @pytest.mark.asyncio
    async def test_product_in_db_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the product in db schema model validate updated"""
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

        model = Products(
            name="Test Product",
            description="Test Product Description",
            category_id=category.id,
            supplier_id=supplier.id
        )
        await save_object(db_session, model)

        query = select(Products).where(Products.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Test Product Updated"
        db_model.description = "Test Product Description Updated"

        db_schema_object = ProductInDB.model_validate(db_model)
        assert db_schema_object == ProductInDB(
            id=model.id,
            name="Test Product Updated",
            description="Test Product Description Updated",
            slug="test-product-updated",
            category_id=category.id,
            supplier_id=supplier.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )


class TestProductResponse:
    """Test cases for the product response schema"""

    def test_product_response_inheritance(self):
        """Test that the product response schema inherits from ProductInDB"""
        assert issubclass(ProductResponse, ProductInDB)

    def test_product_response_fields_inheritance(self):
        """Test that the product response schema has correct fields"""
        fields = ProductResponse.model_fields
        assert len(fields) == 13
        assert 'name' in fields
        assert 'description' in fields
        assert 'category_id' in fields
        assert 'supplier_id' in fields
        assert 'slug' in fields
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

        category_id = fields['category_id']
        assert category_id.is_required() is True
        assert category_id.annotation == int
        assert category_id.default is PydanticUndefined

        supplier_id = fields['supplier_id']
        assert supplier_id.is_required() is True
        assert supplier_id.annotation == int
        assert supplier_id.default is PydanticUndefined

        slug = fields['slug']
        assert slug.is_required() is True
        assert slug.annotation == str
        assert slug.default is PydanticUndefined

        full_path = fields['full_path']
        assert full_path.is_required() is True
        # Check that it's a List with Annotated Union - exact comparison is complex
        annotation_str = str(full_path.annotation)
        assert annotation_str.startswith('typing.List[typing.Annotated[typing.Union[')
        assert 'discriminator' in str(full_path.annotation)
        assert full_path.default is PydanticUndefined

        model_config = ProductResponse.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_product_response_model_validate(self, db_session: AsyncSession):
        """Test that the product response schema model validate"""
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

        model = Products(
            name="Test Product",
            description="Test Product Description",
            category_id=child_category.id,
            supplier_id=supplier.id
        )
        await save_object(db_session, model)

        query = (
            select(Products)
            .where(Products.id == model.id)
            .options(
                selectinload(Products.category)
                .selectinload(Categories.parent)
                .selectinload(Categories.category_type)
            )
        )
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = ProductResponse.model_validate(db_model)

        assert db_schema_object == ProductResponse(
            id=model.id,
            name="Test Product",
            description="Test Product Description",
            slug="test-product",
            category_id=child_category.id,
            supplier_id=supplier.id,
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
    async def test_product_response_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the product response schema model validate updated"""
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

        model = Products(
            name="Test Product",
            description="Test Product Description",
            category_id=child_category.id,
            supplier_id=supplier.id
        )
        await save_object(db_session, model)

        query = (
            select(Products)
            .where(Products.id == model.id)
            .options(
                selectinload(Products.category)
                .selectinload(Categories.parent)
                .selectinload(Categories.category_type)
            )
        )
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.full_path[0]['name'] = "Full Path Parent Category Updated"
        db_model.full_path[1]['name'] = "Full Path Child Category Updated"
        db_model.full_path[2]['name'] = "Full Path Product Updated"

        # Full path is just a property. Even if we update the full path, when model
        # validate is called, the full path will be recomputed and got normal value

        db_schema_object = ProductResponse.model_validate(db_model)
        assert db_schema_object == ProductResponse(
            id=model.id,
            name="Test Product",
            description="Test Product Description",
            slug="test-product",
            category_id=child_category.id,
            supplier_id=supplier.id,
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
                )
            ],
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )
