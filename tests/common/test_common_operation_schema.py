from pydantic import BaseModel, Field, ValidationError
from typing import Optional

import pytest
import json


class SimpleTestSchema(BaseModel):
    """Simple schema for testing with 5 different field patterns"""

    # Pattern 1: nama_field: tipe_data
    name: str

    # Pattern 2: nama_field: Optional[tipe_data]
    description: Optional[str] = None

    # Pattern 3: nama_field: tipe_data = Field(..., metadata)
    price: float = Field(..., description="Product price", gt=0)

    # Pattern 4: nama_field: Optional[tipe_data] = Field(metadata)
    category: Optional[str] = Field(
        default=None, description="Product category", max_length=50
    )

    # Pattern 5: nama_field: tipe_data = nilai
    status: str = "active"


class TestCommonOperationSchema:
    """Test cases for SimpleTestSchema"""

    def test_schema_with_all_fields_provided(self):
        """Test schema with all fields given values"""
        # Arrange
        data = {
            "name": "Test Product",
            "description": "A test product description",
            "price": 99.99,
            "category": "Electronics",
            "status": "inactive"
        }

        # Act
        schema = SimpleTestSchema(**data)

        # Assert
        assert schema.name == "Test Product"
        assert schema.description == "A test product description"
        assert schema.price == 99.99
        assert schema.category == "Electronics"
        assert schema.status == "inactive"

    def test_schema_with_only_required_fields(self):
        """Test schema with only required fields provided"""
        # Arrange
        data = {
            "name": "Test Product",
            "price": 49.99
        }

        # Act
        schema = SimpleTestSchema(**data)

        # Assert
        assert schema.name == "Test Product"
        assert schema.description is None
        assert schema.price == 49.99
        assert schema.category is None
        assert schema.status == "active"  # default value

    def test_schema_with_partial_required_fields_should_error(self):
        """Test schema with only some required fields - should raise ValidationError"""
        # Arrange
        data = {
            "name": "Test Product",
            "description": "Some description",
            # Missing required 'price' field
            "category": "Electronics"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            SimpleTestSchema(**data)

        # Verify the error is about missing required field
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "price" in str(errors[0]["loc"])

    def test_schema_with_only_optional_fields_should_error(self):
        """Test schema with only optional fields - should raise ValidationError"""
        # Arrange
        data = {
            "description": "Some description",
            "category": "Electronics"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            SimpleTestSchema(**data)

        # Verify the errors are about missing required fields
        errors = exc_info.value.errors()
        assert len(errors) == 2  # Missing 'name' and 'price'
        error_fields = {error["loc"][0] for error in errors}
        assert "name" in error_fields
        assert "price" in error_fields

    def test_schema_with_no_fields_should_error(self):
        """Test schema with no fields provided - should raise ValidationError"""
        # Arrange
        data = {}

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            SimpleTestSchema(**data)

        # Verify the errors are about missing required fields
        errors = exc_info.value.errors()
        assert len(errors) == 2  # Missing 'name' and 'price'
        error_fields = {error["loc"][0] for error in errors}
        assert "name" in error_fields
        assert "price" in error_fields

    def test_schema_with_null_values_for_optional_fields(self):
        """Test schema with explicit None values for optional fields"""
        # Arrange
        data = {
            "name": "Test Product",
            "price": 49.99,
            "description": None,
            "category": None
        }

        # Act
        schema = SimpleTestSchema(**data)

        # Assert
        assert schema.name == "Test Product"
        assert schema.description is None
        assert schema.price == 49.99
        assert schema.category is None
        assert schema.status == "active"

    def test_schema_with_extra_fields_should_be_ignored(self):
        """Test schema with extra fields that should be ignored"""
        # Arrange
        data = {
            "name": "Test Product",
            "price": 49.99,
            "extra_field": "This should be ignored",
            "another_extra": 123
        }

        # Act
        schema = SimpleTestSchema(**data)

        # Assert
        assert schema.name == "Test Product"
        assert schema.price == 49.99
        assert schema.description is None
        assert schema.category is None
        assert schema.status == "active"
        # Extra fields should not be present in the schema
        assert not hasattr(schema, "extra_field")
        assert not hasattr(schema, "another_extra")

    # Test scenarios for Pydantic methods

    def test_model_validate_with_valid_dict(self):
        """Test model_validate method with valid dictionary"""
        # Arrange
        data = {
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "category": "Electronics",
            "status": "active"
        }

        # Act
        schema = SimpleTestSchema.model_validate(data)

        # Assert
        assert isinstance(schema, SimpleTestSchema)
        assert schema.name == "Test Product"
        assert schema.description == "A test product"
        assert schema.price == 99.99
        assert schema.category == "Electronics"
        assert schema.status == "active"

    def test_model_validate_with_minimal_required_fields(self):
        """Test model_validate method with only required fields"""
        # Arrange
        data = {
            "name": "Test Product",
            "price": 49.99
        }

        # Act
        schema = SimpleTestSchema.model_validate(data)

        # Assert
        assert isinstance(schema, SimpleTestSchema)
        assert schema.name == "Test Product"
        assert schema.price == 49.99
        assert schema.description is None
        assert schema.category is None
        assert schema.status == "active"

    def test_model_validate_with_invalid_data_should_error(self):
        """Test model_validate method with invalid data should raise ValidationError"""
        # Arrange
        data = {
            "name": "Test Product"
            # Missing required 'price' field
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            SimpleTestSchema.model_validate(data)

        # Verify validation error
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "price" in str(errors[0]["loc"])

    def test_model_validate_from_existing_instance(self):
        """Test model_validate method with existing schema instance"""
        # Arrange
        original_data = {
            "name": "Test Product",
            "price": 99.99,
            "description": "Original description"
        }
        original_schema = SimpleTestSchema(**original_data)

        # Act
        validated_schema = SimpleTestSchema.model_validate(original_schema)

        # Assert
        assert isinstance(validated_schema, SimpleTestSchema)
        assert validated_schema.name == "Test Product"
        assert validated_schema.price == 99.99
        assert validated_schema.description == "Original description"
        # Should be a new instance
        assert validated_schema is original_schema

    def test_model_dump_with_all_fields(self):
        """Test model_dump method returns correct dictionary"""
        # Arrange
        data = {
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "category": "Electronics",
            "status": "inactive"
        }
        schema = SimpleTestSchema(**data)

        # Act
        dumped_data = schema.model_dump()

        # Assert
        assert isinstance(dumped_data, dict)
        assert dumped_data == data
        assert dumped_data["name"] == "Test Product"
        assert dumped_data["description"] == "A test product"
        assert dumped_data["price"] == 99.99
        assert dumped_data["category"] == "Electronics"
        assert dumped_data["status"] == "inactive"

    def test_model_dump_with_minimal_fields(self):
        """Test model_dump method with minimal required fields"""
        # Arrange
        data = {
            "name": "Test Product",
            "price": 49.99
        }
        schema = SimpleTestSchema(**data)

        # Act
        dumped_data = schema.model_dump()

        # Assert
        expected_data = {
            "name": "Test Product",
            "description": None,
            "price": 49.99,
            "category": None,
            "status": "active"
        }
        assert isinstance(dumped_data, dict)
        assert dumped_data == expected_data

    def test_model_dump_exclude_fields(self):
        """Test model_dump method with excluded fields"""
        # Arrange
        data = {
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "category": "Electronics",
            "status": "active"
        }
        schema = SimpleTestSchema(**data)

        # Act
        dumped_data = schema.model_dump(exclude={"description", "category"})

        # Assert
        expected_data = {
            "name": "Test Product",
            "price": 99.99,
            "status": "active"
        }
        assert isinstance(dumped_data, dict)
        assert dumped_data == expected_data
        assert "description" not in dumped_data
        assert "category" not in dumped_data

    def test_model_dump_exclude_none_values(self):
        """Test model_dump method excluding None values"""
        # Arrange
        data = {
            "name": "Test Product",
            "price": 49.99
            # description and category will be None
        }
        schema = SimpleTestSchema(**data)

        # Act
        dumped_data = schema.model_dump(exclude_none=True)

        # Assert
        expected_data = {
            "name": "Test Product",
            "price": 49.99,
            "status": "active"
        }
        assert isinstance(dumped_data, dict)
        assert dumped_data == expected_data
        assert "description" not in dumped_data
        assert "category" not in dumped_data

    def test_model_dump_json_with_all_fields(self):
        """Test model_dump_json method returns valid JSON string"""
        # Arrange
        data = {
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "category": "Electronics",
            "status": "active"
        }
        schema = SimpleTestSchema(**data)

        # Act
        json_string = schema.model_dump_json()

        # Assert
        assert isinstance(json_string, str)
        # Parse JSON to verify it's valid
        parsed_data = json.loads(json_string)
        assert parsed_data == data

    def test_model_dump_json_with_minimal_fields(self):
        """Test model_dump_json method with minimal required fields"""
        # Arrange
        data = {
            "name": "Test Product",
            "price": 49.99
        }
        schema = SimpleTestSchema(**data)

        # Act
        json_string = schema.model_dump_json()

        # Assert
        assert isinstance(json_string, str)
        # Parse JSON to verify it's valid
        parsed_data = json.loads(json_string)
        expected_data = {
            "name": "Test Product",
            "description": None,
            "price": 49.99,
            "category": None,
            "status": "active"
        }
        assert parsed_data == expected_data

    def test_model_dump_json_exclude_none_values(self):
        """Test model_dump_json method excluding None values"""
        # Arrange
        data = {
            "name": "Test Product",
            "price": 49.99
            # description and category will be None
        }
        schema = SimpleTestSchema(**data)

        # Act
        json_string = schema.model_dump_json(exclude_none=True)

        # Assert
        assert isinstance(json_string, str)
        # Parse JSON to verify it's valid
        parsed_data = json.loads(json_string)
        expected_data = {
            "name": "Test Product",
            "price": 49.99,
            "status": "active"
        }
        assert parsed_data == expected_data
        assert "description" not in parsed_data
        assert "category" not in parsed_data

    def test_model_dump_json_with_custom_formatting(self):
        """Test model_dump_json method with custom JSON formatting"""
        # Arrange
        data = {
            "name": "Test Product",
            "price": 99.99
        }
        schema = SimpleTestSchema(**data)

        # Act
        json_string = schema.model_dump_json(indent=2)

        # Assert
        assert isinstance(json_string, str)
        # Should contain indentation (newlines and spaces)
        assert "\n" in json_string
        assert "  " in json_string  # 2-space indentation

        # Parse JSON to verify it's still valid
        parsed_data = json.loads(json_string)
        expected_data = {
            "name": "Test Product",
            "description": None,
            "price": 99.99,
            "category": None,
            "status": "active"
        }
        assert parsed_data == expected_data

    def test_roundtrip_model_dump_and_validate(self):
        """Test roundtrip: create schema -> dump -> validate -> should be identical"""
        # Arrange
        original_data = {
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "category": "Electronics",
            "status": "active"
        }

        # Act
        original_schema = SimpleTestSchema(**original_data)
        dumped_data = original_schema.model_dump()
        reconstructed_schema = SimpleTestSchema.model_validate(dumped_data)

        # Assert
        assert original_schema.name == reconstructed_schema.name
        assert original_schema.description == reconstructed_schema.description
        assert original_schema.price == reconstructed_schema.price
        assert original_schema.category == reconstructed_schema.category
        assert original_schema.status == reconstructed_schema.status

        # Verify they produce the same dump
        assert original_schema.model_dump() == reconstructed_schema.model_dump()

    def test_roundtrip_json_serialization(self):
        """Test roundtrip: schema -> JSON -> parse -> validate -> should be identical"""
        # Arrange
        original_data = {
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "category": "Electronics",
            "status": "active"
        }

        # Act
        original_schema = SimpleTestSchema(**original_data)
        json_string = original_schema.model_dump_json()

        parsed_data = json.loads(json_string)
        reconstructed_schema = SimpleTestSchema.model_validate(parsed_data)

        # Assert
        assert original_schema.name == reconstructed_schema.name
        assert original_schema.description == reconstructed_schema.description
        assert original_schema.price == reconstructed_schema.price
        assert original_schema.category == reconstructed_schema.category
        assert original_schema.status == reconstructed_schema.status
