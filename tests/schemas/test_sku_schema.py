from typing import Optional, Literal, List
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import StrictStr
from pydantic_core import PydanticUndefined
import pytest

from app.schemas.base import (
    BaseSchema, BaseInDB, BaseCreateSchema, BaseUpdateSchema,
    StrictPositiveInt, PositiveDecimal
)
from app.schemas.sku_schema import (
    SkuBase, SkuCreate,
    SkuUpdate, SkuInDB,
    SkuResponse, SkuPathItem,
    PriceDetailCreate, PriceDetailUpdate,
    AttributeValueInput, PricelistSummary,
    PriceDetailSummary, AttributeSummary,
    AttributeValueSummary
)
from app.schemas.category_schema import CategoryPathItem
from app.schemas.product_schema import ProductPathItem
from app.models import (
    Skus, Products, Categories, Pricelists, PriceDetails, Attributes,
    SkuAttributeValue
)
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


class TestPriceDetailCreate:
    """Test cases for the price detail create schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.price_detail_create_dict = {
            "pricelist_id": 1,
            "price": 100000,
            "minimum_quantity": 1
        }

    def test_price_detail_create_schema_inheritance(self):
        """Test that the price detail create schema inherits from BaseSchema"""
        assert issubclass(PriceDetailCreate, BaseSchema)

    def test_price_detail_create_fields_inheritance(self):
        """Test that the price detail create schema has correct fields"""
        fields = PriceDetailCreate.model_fields
        assert len(fields) == 3
        assert 'pricelist_id' in fields
        assert 'price' in fields
        assert 'minimum_quantity' in fields

        pricelist_id = fields['pricelist_id']
        assert pricelist_id.is_required() is True
        assert pricelist_id.annotation == int
        assert pricelist_id.default is PydanticUndefined
        assert pricelist_id.metadata[0].strict is True
        assert pricelist_id.metadata[1].gt == 0

        price = fields['price']
        assert price.is_required() is True
        assert price.annotation == Decimal
        assert price.default is PydanticUndefined
        assert price.metadata[0].func is not None
        assert price.metadata[1].gt == 0

        minimum_quantity = fields['minimum_quantity']
        assert minimum_quantity.is_required() is True
        assert minimum_quantity.annotation == int
        assert minimum_quantity.default is PydanticUndefined
        assert minimum_quantity.metadata[0].strict is True
        assert minimum_quantity.metadata[1].gt == 0

    def test_price_detail_create_schema_input(self):
        schema = PriceDetailCreate(**self.price_detail_create_dict)
        assert schema.pricelist_id == 1
        assert schema.price == 100000
        assert schema.minimum_quantity == 1

    def test_price_detail_create_schema_input_updated(self):
        schema = PriceDetailCreate(**self.price_detail_create_dict)
        assert schema.pricelist_id == 1
        assert schema.price == 100000
        assert schema.minimum_quantity == 1

        schema.price = 150000
        assert schema.price == 150000

    def test_price_detail_create_schema_model_dump(self):
        schema = PriceDetailCreate(**self.price_detail_create_dict)
        assert schema.model_dump() == {
            "pricelist_id": 1,
            "price": 100000,
            "minimum_quantity": 1
        }

    def test_price_detail_create_schema_model_dump_json(self):
        schema = PriceDetailCreate(**self.price_detail_create_dict)
        assert schema.model_dump_json() == '{'\
            '"pricelist_id":1,'\
            '"price":"100000.00",'\
            '"minimum_quantity":1'\
            '}'


class TestAttributeValueInput:
    """Test cases for the attribute value input schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.attribute_value_input_dict = {
            "attribute_id": 1,
            "value": "Test Attribute Value"
        }

    def test_attribute_value_input_schema_inheritance(self):
        """Test that the attribute value input schema inherits from BaseSchema"""
        assert issubclass(AttributeValueInput, BaseSchema)

    def test_attribute_value_input_fields_inheritance(self):
        """Test that the attribute value input schema has correct fields"""
        fields = AttributeValueInput.model_fields
        assert len(fields) == 2
        assert 'attribute_id' in fields
        assert 'value' in fields

        attribute_id = fields['attribute_id']
        assert attribute_id.is_required() is True
        assert attribute_id.annotation == int
        assert attribute_id.default is PydanticUndefined
        assert attribute_id.metadata[0].strict is True
        assert attribute_id.metadata[1].gt == 0

        value = fields['value']
        assert value.is_required() is True
        assert value.annotation == str
        assert value.default is PydanticUndefined
        assert value.metadata[0].min_length == 1
        assert value.metadata[1].max_length == 50

    def test_attribute_value_input_schema_input(self):
        schema = AttributeValueInput(**self.attribute_value_input_dict)
        assert schema.attribute_id == 1
        assert schema.value == "Test Attribute Value"

    def test_attribute_value_input_schema_input_updated(self):
        schema = AttributeValueInput(**self.attribute_value_input_dict)
        assert schema.attribute_id == 1
        assert schema.value == "Test Attribute Value"

        schema.value = "Test Attribute Value Updated"
        assert schema.value == "Test Attribute Value Updated"

    def test_attribute_value_input_schema_model_dump(self):
        schema = AttributeValueInput(**self.attribute_value_input_dict)
        assert schema.model_dump() == {
            "attribute_id": 1,
            "value": "Test Attribute Value"
        }

    def test_attribute_value_input_schema_model_dump_json(self):
        schema = AttributeValueInput(**self.attribute_value_input_dict)
        assert schema.model_dump_json() == '{'\
            '"attribute_id":1,'\
            '"value":"Test Attribute Value"'\
            '}'


class TestSkuCreate:
    """Test cases for the SKU create schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.sku_dict = {
            "name": "Test SKU",
            "description": "Test SKU Description",
            "product_id": 1,
            "price_details": [
                {
                    "pricelist_id": 1,
                    "price": 100000,
                    "minimum_quantity": 1
                },
                {
                    "pricelist_id": 2,
                    "price": 150000,
                    "minimum_quantity": 2
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": 1,
                    "value": "Test Attribute Value"
                },
                {
                    "attribute_id": 2,
                    "value": "Test Attribute Value 2"
                }
            ]
        }

    def test_sku_create_schema_inheritance(self):
        """Test that the SKU create schema inherits from BaseCreateSchema"""
        assert issubclass(SkuCreate, BaseCreateSchema)
        assert issubclass(SkuCreate, SkuBase)

    def test_sku_create_fields_inheritance(self):
        """Test that the SKU create schema has correct fields"""
        fields = SkuCreate.model_fields
        assert len(fields) == 7
        assert 'name' in fields
        assert 'description' in fields
        assert 'product_id' in fields
        assert 'price_details' in fields
        assert 'attribute_values' in fields

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

        price_details = fields['price_details']
        assert price_details.is_required() is True
        assert price_details.annotation == List[PriceDetailCreate]
        assert price_details.default is PydanticUndefined

        attribute_values = fields['attribute_values']
        assert attribute_values.is_required() is True
        assert attribute_values.annotation == List[AttributeValueInput]
        assert attribute_values.default is PydanticUndefined

    def test_sku_create_schema_input(self):
        schema = SkuCreate(**self.sku_dict)
        assert schema.name == "Test SKU"
        assert schema.description == "Test SKU Description"
        assert schema.product_id == 1
        assert schema.price_details == [
            PriceDetailCreate(pricelist_id=1, price=100000, minimum_quantity=1),
            PriceDetailCreate(pricelist_id=2, price=150000, minimum_quantity=2)
        ]
        assert schema.attribute_values == [
            AttributeValueInput(attribute_id=1, value="Test Attribute Value"),
            AttributeValueInput(attribute_id=2, value="Test Attribute Value 2")
        ]

    def test_sku_create_schema_input_updated(self):
        schema = SkuCreate(**self.sku_dict)
        assert schema.name == "Test SKU"
        assert schema.description == "Test SKU Description"
        assert schema.product_id == 1
        assert schema.price_details == [
            PriceDetailCreate(pricelist_id=1, price=100000, minimum_quantity=1),
            PriceDetailCreate(pricelist_id=2, price=150000, minimum_quantity=2)
        ]
        assert schema.attribute_values == [
            AttributeValueInput(attribute_id=1, value="Test Attribute Value"),
            AttributeValueInput(attribute_id=2, value="Test Attribute Value 2")
        ]

        schema.name = "Test SKU Updated"
        schema.price_details = [
            PriceDetailCreate(pricelist_id=3, price=300000, minimum_quantity=3),
        ]
        assert schema.name == "Test SKU Updated"
        assert schema.price_details == [
            PriceDetailCreate(pricelist_id=3, price=300000, minimum_quantity=3),
        ]

    def test_sku_create_schema_model_dump(self):
        schema = SkuCreate(**self.sku_dict)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "name": "Test SKU",
            "description": "Test SKU Description",
            "product_id": 1,
            "price_details": [
                {
                    "pricelist_id": 1,
                    "price": 100000,
                    "minimum_quantity": 1
                },
                {
                    "pricelist_id": 2,
                    "price": 150000,
                    "minimum_quantity": 2
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": 1,
                    "value": "Test Attribute Value"
                },
                {
                    "attribute_id": 2,
                    "value": "Test Attribute Value 2"
                }
            ]
        }

    def test_sku_create_schema_model_dump_json(self):
        schema = SkuCreate(**self.sku_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"name":"Test SKU",'\
            '"description":"Test SKU Description",'\
            '"product_id":1,'\
            '"price_details":['\
            '{"pricelist_id":1,"price":"100000.00","minimum_quantity":1},'\
            '{"pricelist_id":2,"price":"150000.00","minimum_quantity":2}'\
            '],'\
            '"attribute_values":['\
            '{"attribute_id":1,"value":"Test Attribute Value"},'\
            '{"attribute_id":2,"value":"Test Attribute Value 2"}'\
            ']'\
            '}'


class TestPriceDetailUpdate:
    """Test cases for the price detail update schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.price_detail_update_dict = {
            "id": 1,
            "price": 150000,
            "minimum_quantity": 2
        }

    def test_price_detail_update_schema_inheritance(self):
        """Test that the price detail update schema inherits from BaseSchema"""
        assert issubclass(PriceDetailUpdate, BaseSchema)

    def test_price_detail_update_fields_inheritance(self):
        """Test that the price detail update schema has correct fields"""
        fields = PriceDetailUpdate.model_fields
        assert len(fields) == 3
        assert 'id' in fields
        assert 'price' in fields
        assert 'minimum_quantity' in fields

        id = fields['id']
        assert id.is_required() is True
        assert id.annotation == int
        assert id.default is PydanticUndefined
        assert id.metadata[0].strict is True
        assert id.metadata[1].gt == 0

        price = fields['price']
        assert price.is_required() is False
        assert price.annotation == Optional[PositiveDecimal]
        assert price.default is None

        minimum_quantity = fields['minimum_quantity']
        assert minimum_quantity.is_required() is False
        assert minimum_quantity.annotation == Optional[StrictPositiveInt]
        assert minimum_quantity.default is None

    def test_price_detail_update_schema_input(self):
        schema = PriceDetailUpdate(**self.price_detail_update_dict)
        assert schema.id == 1
        assert schema.price == 150000
        assert schema.minimum_quantity == 2

    def test_price_detail_update_schema_input_updated(self):
        schema = PriceDetailUpdate(**self.price_detail_update_dict)
        assert schema.id == 1
        assert schema.price == 150000
        assert schema.minimum_quantity == 2

        schema.price = 200000
        assert schema.price == 200000

    def test_price_detail_update_schema_model_dump(self):
        schema = PriceDetailUpdate(**self.price_detail_update_dict)
        assert schema.model_dump() == {
            "id": 1,
            "price": 150000,
            "minimum_quantity": 2
        }

    def test_price_detail_update_schema_model_dump_json(self):
        schema = PriceDetailUpdate(**self.price_detail_update_dict)
        assert schema.model_dump_json() == '{'\
            '"id":1,'\
            '"price":"150000.00",'\
            '"minimum_quantity":2'\
            '}'


class TestSkuUpdate:
    """Test cases for the SKU update schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.sku_dict = {
            "name": "Test SKU",
            "description": "Test SKU Description",
            "product_id": 1,
            "price_details_to_create": [
                {
                    "pricelist_id": 3,
                    "price": 300000,
                    "minimum_quantity": 3
                }
            ],
            "price_details_to_update": [
                {
                    "id": 1,
                    "price": 150000,
                    "minimum_quantity": 2
                }
            ],
            "price_details_to_delete": [1],
            "attribute_values": [
                {
                    "attribute_id": 1,
                    "value": "Test Attribute Value"
                }
            ]
        }

    def test_sku_update_schema_inheritance(self):
        """Test that the SKU update schema inherits from BaseUpdateSchema"""
        assert issubclass(SkuUpdate, BaseUpdateSchema)
        assert issubclass(SkuUpdate, SkuBase)

    def test_sku_update_fields_inheritance(self):
        """Test that the SKU update schema has correct fields"""
        fields = SkuUpdate.model_fields
        assert len(fields) == 9
        assert 'name' in fields
        assert 'description' in fields
        assert 'product_id' in fields
        assert 'price_details_to_create' in fields
        assert 'price_details_to_update' in fields
        assert 'price_details_to_delete' in fields
        assert 'attribute_values' in fields

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

        price_details_to_create = fields['price_details_to_create']
        assert price_details_to_create.is_required() is False
        assert price_details_to_create.annotation == Optional[List[PriceDetailCreate]]
        assert price_details_to_create.default is None

        price_details_to_update = fields['price_details_to_update']
        assert price_details_to_update.is_required() is False
        assert price_details_to_update.annotation == Optional[List[PriceDetailUpdate]]
        assert price_details_to_update.default is None

        price_details_to_delete = fields['price_details_to_delete']
        assert price_details_to_delete.is_required() is False
        assert price_details_to_delete.annotation == Optional[List[StrictPositiveInt]]
        assert price_details_to_delete.default is None

        attribute_values = fields['attribute_values']
        assert attribute_values.is_required() is False
        assert attribute_values.annotation == Optional[List[AttributeValueInput]]
        assert attribute_values.default is None

    def test_sku_update_schema_input(self):
        schema = SkuUpdate(**self.sku_dict)
        assert schema.name == "Test SKU"
        assert schema.description == "Test SKU Description"
        assert schema.product_id == 1
        assert schema.price_details_to_create == [
            PriceDetailCreate(pricelist_id=3, price=300000, minimum_quantity=3)
        ]
        assert schema.price_details_to_update == [
            PriceDetailUpdate(id=1, price=150000, minimum_quantity=2)
        ]
        assert schema.price_details_to_delete == [1]
        assert schema.attribute_values == [
            AttributeValueInput(attribute_id=1, value="Test Attribute Value")
        ]

    def test_sku_update_schema_input_updated(self):
        schema = SkuUpdate(**self.sku_dict)
        assert schema.name == "Test SKU"
        assert schema.description == "Test SKU Description"
        assert schema.product_id == 1
        assert schema.price_details_to_create == [
            PriceDetailCreate(pricelist_id=3, price=300000, minimum_quantity=3)
        ]
        assert schema.price_details_to_update == [
            PriceDetailUpdate(id=1, price=150000, minimum_quantity=2)
        ]
        assert schema.price_details_to_delete == [1]
        assert schema.attribute_values == [
            AttributeValueInput(attribute_id=1, value="Test Attribute Value")
        ]

        schema.name = "Test SKU Updated"
        schema.price_details_to_delete = [2]
        assert schema.name == "Test SKU Updated"
        assert schema.price_details_to_delete == [2]

    def test_sku_update_schema_model_dump(self):
        schema = SkuUpdate(**self.sku_dict)
        assert schema.model_dump() == {
            "is_active": None,
            "sequence": None,
            "name": "Test SKU",
            "description": "Test SKU Description",
            "product_id": 1,
            "price_details_to_create": [
                {
                    "pricelist_id": 3,
                    "price": 300000,
                    "minimum_quantity": 3
                }
            ],
            "price_details_to_update": [
                {
                    "id": 1,
                    "price": 150000,
                    "minimum_quantity": 2
                }
            ],
            "price_details_to_delete": [1],
            "attribute_values": [
                {
                    "attribute_id": 1,
                    "value": "Test Attribute Value"
                }
            ]
        }

    def test_sku_update_schema_model_dump_json(self):
        schema = SkuUpdate(**self.sku_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":null,'\
            '"sequence":null,'\
            '"name":"Test SKU",'\
            '"description":"Test SKU Description",'\
            '"product_id":1,'\
            '"price_details_to_create":['\
            '{"pricelist_id":3,"price":"300000.00","minimum_quantity":3}'\
            '],'\
            '"price_details_to_update":['\
            '{"id":1,"price":"150000.00","minimum_quantity":2}'\
            '],'\
            '"price_details_to_delete":[1],'\
            '"attribute_values":['\
            '{"attribute_id":1,"value":"Test Attribute Value"}'\
            ']'\
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
    async def test_sku_in_db_model_validate(
        self, db_session: AsyncSession, product_factory
    ):
        """Test that the SKU in db schema model validate"""
        product = await product_factory()

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
        self, db_session: AsyncSession, product_factory
    ):
        """Test that the SKU in db schema model validate updated"""
        product = await product_factory()

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


class TestPricelistSummary:
    """Test cases for the pricelist summary schema"""

    def test_pricelist_summary_schema_inheritance(self):
        """Test that the pricelist summary schema inherits from BaseSchema"""
        assert issubclass(PricelistSummary, BaseSchema)

    def test_pricelist_summary_fields_inheritance(self):
        """Test that the pricelist summary schema has correct fields"""
        fields = PricelistSummary.model_fields
        assert len(fields) == 3
        assert 'id' in fields
        assert 'name' in fields
        assert 'code' in fields

        id = fields['id']
        assert id.is_required() is True
        assert id.annotation == int
        assert id.default is PydanticUndefined

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined

        code = fields['code']
        assert code.is_required() is True
        assert code.annotation == str
        assert code.default is PydanticUndefined

        model_config = PricelistSummary.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_pricelist_summary_schema_model_validate(
        self, db_session: AsyncSession
    ):
        """Test that the pricelist summary schema model validate"""
        pricelist = Pricelists(name="Test Pricelist")
        await save_object(db_session, pricelist)

        query = select(Pricelists).where(Pricelists.id == pricelist.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = PricelistSummary.model_validate(db_model)
        assert db_schema_object == PricelistSummary(
            id=pricelist.id,
            name="Test Pricelist",
            code="TEST-PRICELIST"
        )

    @pytest.mark.asyncio
    async def test_pricelist_summary_schema_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the pricelist summary schema model validate"""
        pricelist = Pricelists(name="Test Pricelist")
        await save_object(db_session, pricelist)

        query = select(Pricelists).where(Pricelists.id == pricelist.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Test Pricelist Updated"

        db_schema_object = PricelistSummary.model_validate(db_model)
        assert db_schema_object == PricelistSummary(
            id=pricelist.id,
            name="Test Pricelist Updated",
            code="TEST-PRICELIST-UPDATED"
        )


class TestPriceDetailSummary:
    """Test cases for the price detail summary schema"""

    def test_price_detail_summary_schema_inheritance(self):
        """Test that the price detail summary schema inherits from BaseSchema"""
        assert issubclass(PriceDetailSummary, BaseSchema)

    def test_price_detail_summary_fields_inheritance(self):
        """Test that the price detail summary schema has correct fields"""
        fields = PriceDetailSummary.model_fields
        assert len(fields) == 4
        assert 'id' in fields
        assert 'price' in fields
        assert 'minimum_quantity' in fields
        assert 'pricelist' in fields

        id = fields['id']
        assert id.is_required() is True
        assert id.annotation == int
        assert id.default is PydanticUndefined

        price = fields['price']
        assert price.is_required() is True
        assert price.annotation == Decimal
        assert price.default is PydanticUndefined
        assert price.metadata[0].func is not None
        assert price.metadata[1].gt == 0

        minimum_quantity = fields['minimum_quantity']
        assert minimum_quantity.is_required() is True
        assert minimum_quantity.annotation == int
        assert minimum_quantity.default is PydanticUndefined

        pricelist = fields['pricelist']
        assert pricelist.is_required() is True
        assert pricelist.annotation == PricelistSummary
        assert pricelist.default is PydanticUndefined

    @pytest.mark.asyncio
    async def test_price_detail_summary_schema_model_validate(
        self, db_session: AsyncSession, pricelist_factory, sku_factory
    ):
        """Test that the price detail summary schema model validate"""
        pricelist = await pricelist_factory()

        sku = await sku_factory()

        price_detail = PriceDetails(
            pricelist_id=pricelist.id,
            price=100000,
            minimum_quantity=1,
            sku_id=sku.id
        )
        await save_object(db_session, price_detail)

        query = select(PriceDetails).where(PriceDetails.id == price_detail.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = PriceDetailSummary.model_validate(db_model)
        assert db_schema_object == PriceDetailSummary(
            id=price_detail.id,
            price=100000,
            minimum_quantity=1,
            pricelist=PricelistSummary(
                id=pricelist.id,
                name="Test Pricelist",
                code="TEST-PRICELIST"
            )
        )

    @pytest.mark.asyncio
    async def test_price_detail_summary_schema_model_validate_updated(
        self, db_session: AsyncSession, pricelist_factory, sku_factory
    ):
        """Test that the price detail summary schema model validate updated"""
        pricelist = await pricelist_factory()

        sku = await sku_factory()

        price_detail = PriceDetails(
            pricelist_id=pricelist.id,
            price=100000,
            minimum_quantity=1,
            sku_id=sku.id
        )
        await save_object(db_session, price_detail)

        query = select(PriceDetails).where(PriceDetails.id == price_detail.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.price = 150000
        db_model.minimum_quantity = 2

        db_schema_object = PriceDetailSummary.model_validate(db_model)
        assert db_schema_object == PriceDetailSummary(
            id=price_detail.id,
            price=150000,
            minimum_quantity=2,
            pricelist=PricelistSummary(
                id=pricelist.id,
                name="Test Pricelist",
                code="TEST-PRICELIST",
            )
        )


class TestAttributeSummary:
    """Test cases for the attribute summary schema"""

    def test_attribute_summary_schema_inheritance(self):
        """Test that the attribute summary schema inherits from BaseSchema"""
        assert issubclass(AttributeSummary, BaseSchema)

    def test_attribute_summary_fields_inheritance(self):
        """Test that the attribute summary schema has correct fields"""
        fields = AttributeSummary.model_fields
        assert len(fields) == 5
        assert 'id' in fields
        assert 'name' in fields
        assert 'code' in fields
        assert 'data_type' in fields
        assert 'uom' in fields

        id = fields['id']
        assert id.is_required() is True
        assert id.annotation == int
        assert id.default is PydanticUndefined

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined

        code = fields['code']
        assert code.is_required() is True
        assert code.annotation == str
        assert code.default is PydanticUndefined

        data_type = fields['data_type']
        assert data_type.is_required() is True
        assert data_type.annotation == str
        assert data_type.default is PydanticUndefined

        uom = fields['uom']
        assert uom.is_required() is False
        assert uom.annotation == Optional[str]
        assert uom.default is None

        model_config = AttributeSummary.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_attribute_summary_schema_model_validate(
        self, db_session: AsyncSession
    ):
        """Test that the attribute summary schema model validate"""
        attribute = Attributes(name="Test Attribute", data_type="TEXT", uom="ml")
        await save_object(db_session, attribute)

        query = select(Attributes).where(Attributes.id == attribute.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = AttributeSummary.model_validate(db_model)
        assert db_schema_object == AttributeSummary(
            id=attribute.id,
            name="Test Attribute",
            code="TEST-ATTRIBUTE",
            data_type="TEXT",
            uom="ml"
        )

    @pytest.mark.asyncio
    async def test_attribute_summary_schema_model_validate_updated(
        self, db_session: AsyncSession
    ):
        """Test that the attribute summary schema model validate updated"""
        attribute = Attributes(name="Test Attribute", data_type="TEXT", uom="ml")
        await save_object(db_session, attribute)

        query = select(Attributes).where(Attributes.id == attribute.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.name = "Test Attribute Updated"
        db_model.data_type = "NUMBER"
        db_model.uom = "ml"

        db_schema_object = AttributeSummary.model_validate(db_model)
        assert db_schema_object == AttributeSummary(
            id=attribute.id,
            name="Test Attribute Updated",
            code="TEST-ATTRIBUTE-UPDATED",
            data_type="NUMBER",
            uom="ml"
        )


class TestAttributeValueSummary:
    """Test cases for the attribute value summary schema"""

    def test_attribute_value_summary_schema_inheritance(self):
        """Test that the attribute value summary schema inherits from BaseSchema"""
        assert issubclass(AttributeValueSummary, BaseSchema)

    def test_attribute_value_summary_fields_inheritance(self):
        """Test that the attribute value summary schema has correct fields"""
        fields = AttributeValueSummary.model_fields
        assert len(fields) == 2
        assert 'attribute' in fields
        assert 'value' in fields

        attribute = fields['attribute']
        assert attribute.is_required() is True
        assert attribute.annotation == AttributeSummary
        assert attribute.default is PydanticUndefined

        value = fields['value']
        assert value.is_required() is True
        assert value.annotation == str
        assert value.default is PydanticUndefined

        model_config = AttributeValueSummary.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_attribute_value_summary_schema_model_validate(
        self, db_session: AsyncSession, attribute_factory, sku_factory
    ):
        """Test that the attribute value summary schema model validate"""
        attribute = await attribute_factory()
        sku = await sku_factory()

        attribute_value = SkuAttributeValue(
            attribute_id=attribute.id,
            value="Test Attribute Value",
            sku_id=sku.id
        )
        await save_object(db_session, attribute_value)

        query = select(SkuAttributeValue).where(
            SkuAttributeValue.id == attribute_value.id
        )
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = AttributeValueSummary.model_validate(db_model)

        assert db_schema_object == AttributeValueSummary(
            attribute=AttributeSummary(
                id=attribute.id,
                name="Test Attribute",
                code="TEST-ATTRIBUTE",
                data_type="TEXT",
                uom=None
            ),
            value="Test Attribute Value"
        )

    @pytest.mark.asyncio
    async def test_attribute_value_summary_schema_model_validate_updated(
        self, db_session: AsyncSession, attribute_factory, sku_factory
    ):
        """Test that the attribute value summary schema model validate updated"""
        attribute = await attribute_factory()
        sku = await sku_factory()

        attribute_value = SkuAttributeValue(
            attribute_id=attribute.id,
            value="Test Attribute Value",
            sku_id=sku.id
        )
        await save_object(db_session, attribute_value)

        query = select(SkuAttributeValue).where(
            SkuAttributeValue.id == attribute_value.id
        )
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.value = "Test Attribute Value Updated"

        db_schema_object = AttributeValueSummary.model_validate(db_model)

        assert db_schema_object == AttributeValueSummary(
            attribute=AttributeSummary(
                id=attribute.id,
                name="Test Attribute",
                code="TEST-ATTRIBUTE",
                data_type="TEXT",
                uom=None
            ),
            value="Test Attribute Value Updated"
        )


class TestSkuResponse:
    """Test cases for the SKU response schema"""

    def test_sku_response_inheritance(self):
        """Test that the SKU response schema inherits from SkuInDB"""
        assert issubclass(SkuResponse, SkuInDB)

    def test_sku_response_fields_inheritance(self):
        """Test that the SKU response schema has correct fields"""
        fields = SkuResponse.model_fields
        assert len(fields) == 15
        assert 'name' in fields
        assert 'description' in fields
        assert 'product_id' in fields
        assert 'slug' in fields
        assert 'sku_number' in fields
        assert 'full_path' in fields
        assert 'price_details' in fields
        assert 'attribute_values' in fields

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

        price_details = fields['price_details']
        assert price_details.is_required() is True
        assert price_details.annotation == List[PriceDetailSummary]
        assert price_details.default is PydanticUndefined

        attribute_values = fields['attribute_values']
        assert attribute_values.is_required() is True
        assert attribute_values.annotation == List[AttributeValueSummary]
        assert attribute_values.default is PydanticUndefined
        assert attribute_values.alias == 'sku_attribute_values'

        model_config = SkuResponse.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_sku_response_model_validate(
        self, db_session: AsyncSession, category_type_factory, supplier_factory,
        pricelist_factory, attribute_factory
    ):
        """Test that the SKU response schema model validate"""
        category_type = await category_type_factory()

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

        supplier = await supplier_factory()

        product = Products(
            name="Test Product",
            description="Test Product Description",
            category_id=child_category.id,
            supplier_id=supplier.id
        )
        await save_object(db_session, product)

        pricelist = await pricelist_factory()

        attribute = await attribute_factory()
        attribute2 = await attribute_factory(name="Test Attribute 2")

        model = Skus(
            name="Test SKU",
            description="Test SKU Description",
            product_id=product.id,
            price_details=[
                PriceDetails(
                    pricelist_id=pricelist.id,
                    price=100000,
                    minimum_quantity=1
                ),
                PriceDetails(
                    pricelist_id=pricelist.id,
                    price=150000,
                    minimum_quantity=2
                )
            ],
            sku_attribute_values=[
                SkuAttributeValue(
                    attribute_id=attribute.id,
                    value="Test Attribute Value"
                ),
                SkuAttributeValue(
                    attribute_id=attribute2.id,
                    value="Test Attribute Value 2"
                )
            ]
        )
        await save_object(db_session, model)

        query = select(Skus).where(Skus.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        await db_session.refresh(db_model, ['sku_attribute_values', 'price_details'])

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
            price_details=[
                PriceDetailSummary(
                    id=model.price_details[0].id,
                    price=100000,
                    minimum_quantity=1,
                    pricelist=PricelistSummary(
                        id=pricelist.id,
                        name="Test Pricelist",
                        code="TEST-PRICELIST"
                    )
                ),
                PriceDetailSummary(
                    id=model.price_details[1].id,
                    price=150000,
                    minimum_quantity=2,
                    pricelist=PricelistSummary(
                        id=pricelist.id,
                        name="Test Pricelist",
                        code="TEST-PRICELIST"
                    )
                )
            ],
            sku_attribute_values=[
                AttributeValueSummary(
                    attribute=AttributeSummary(
                        id=attribute.id,
                        name="Test Attribute",
                        code="TEST-ATTRIBUTE",
                        data_type="TEXT",
                        uom=None
                    ),
                    value="Test Attribute Value"
                ),
                AttributeValueSummary(
                    attribute=AttributeSummary(
                        id=attribute2.id,
                        name="Test Attribute 2",
                        code="TEST-ATTRIBUTE-2",
                        data_type="TEXT",
                        uom=None
                    ),
                    value="Test Attribute Value 2"
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
        self, db_session: AsyncSession, category_type_factory, supplier_factory,
        pricelist_factory, attribute_factory
    ):
        """Test that the SKU response schema model validate"""
        category_type = await category_type_factory()

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

        supplier = await supplier_factory()

        product = Products(
            name="Test Product",
            description="Test Product Description",
            category_id=child_category.id,
            supplier_id=supplier.id
        )
        await save_object(db_session, product)

        pricelist = await pricelist_factory()

        attribute = await attribute_factory()
        attribute2 = await attribute_factory(name="Test Attribute 2")

        model = Skus(
            name="Test SKU",
            description="Test SKU Description",
            product_id=product.id,
            price_details=[
                PriceDetails(
                    pricelist_id=pricelist.id,
                    price=100000,
                    minimum_quantity=1
                ),
                PriceDetails(
                    pricelist_id=pricelist.id,
                    price=150000,
                    minimum_quantity=2
                )
            ],
            sku_attribute_values=[
                SkuAttributeValue(
                    attribute_id=attribute.id,
                    value="Test Attribute Value"
                ),
                SkuAttributeValue(
                    attribute_id=attribute2.id,
                    value="Test Attribute Value 2"
                )
            ]
        )
        await save_object(db_session, model)

        query = select(Skus).where(Skus.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        await db_session.refresh(db_model, ['sku_attribute_values', 'price_details'])

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
            price_details=[
                PriceDetailSummary(
                    id=model.price_details[0].id,
                    price=100000,
                    minimum_quantity=1,
                    pricelist=PricelistSummary(
                        id=pricelist.id,
                        name="Test Pricelist",
                        code="TEST-PRICELIST"
                    )
                ),
                PriceDetailSummary(
                    id=model.price_details[1].id,
                    price=150000,
                    minimum_quantity=2,
                    pricelist=PricelistSummary(
                        id=pricelist.id,
                        name="Test Pricelist",
                        code="TEST-PRICELIST"
                    )
                )
            ],
            sku_attribute_values=[
                AttributeValueSummary(
                    attribute=AttributeSummary(
                        id=attribute.id,
                        name="Test Attribute",
                        code="TEST-ATTRIBUTE",
                        data_type="TEXT",
                        uom=None
                    ),
                    value="Test Attribute Value"
                ),
                AttributeValueSummary(
                    attribute=AttributeSummary(
                        id=attribute2.id,
                        name="Test Attribute 2",
                        code="TEST-ATTRIBUTE-2",
                        data_type="TEXT",
                        uom=None
                    ),
                    value="Test Attribute Value 2"
                )
            ],
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_active=True,
            sequence=0
        )
