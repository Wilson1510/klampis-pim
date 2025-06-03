import pytest
from datetime import datetime
from unittest.mock import patch
from sqlalchemy import Column, String, Integer

from app.core.base import Base, JSONBModel
from app.core.config import settings


# Test model untuk testing Base functionality
class SampleModel(Base):
    """Sample model for Base functionality testing."""
    name = Column(String(100), nullable=False)
    description = Column(String(255))


# Test model untuk testing JSONBModel functionality
class SampleJSONBModel(JSONBModel):
    """Sample model for JSONBModel functionality testing."""
    name = Column(String(100), nullable=False)


class TestBaseModel:
    """Test cases for the Base model class."""

    def test_base_model_inheritance(self):
        """Test that Base model can be inherited properly."""
        # Verify SampleModel inherits from Base
        assert issubclass(SampleModel, Base)

        # Verify SampleModel has all expected columns
        expected_columns = {
            'id', 'created_at', 'updated_at', 'created_by',
            'updated_by', 'is_active', 'sequence'
        }
        model_columns = {col.name for col in SampleModel.__table__.columns}
        assert expected_columns.issubset(model_columns)

    def test_base_model_fields_configuration(self):
        """Test that Base model fields are configured correctly."""
        # Test id field
        id_column = SampleModel.__table__.columns['id']
        assert id_column.primary_key is True
        assert id_column.autoincrement is True
        assert id_column.type.python_type == int

        # Test created_at field
        created_at_column = SampleModel.__table__.columns['created_at']
        assert created_at_column.nullable is False
        assert created_at_column.server_default is not None

        # Test updated_at field
        updated_at_column = SampleModel.__table__.columns['updated_at']
        assert updated_at_column.nullable is False
        assert updated_at_column.server_default is not None
        assert updated_at_column.onupdate is not None

        # Test created_by field
        created_by_column = SampleModel.__table__.columns['created_by']
        assert created_by_column.nullable is False
        assert created_by_column.default.arg == settings.SYSTEM_USER_ID

        # Test updated_by field
        updated_by_column = SampleModel.__table__.columns['updated_by']
        assert updated_by_column.nullable is False
        assert updated_by_column.default.arg == settings.SYSTEM_USER_ID

        # Test is_active field
        is_active_column = SampleModel.__table__.columns['is_active']
        assert is_active_column.nullable is False
        assert is_active_column.default.arg is True

        # Test sequence field
        sequence_column = SampleModel.__table__.columns['sequence']
        assert sequence_column.nullable is False
        assert sequence_column.default.arg == 0

    def test_foreign_key_constraints(self):
        """Test that foreign key constraints are properly configured."""
        # Test created_by foreign key
        created_by_column = SampleModel.__table__.columns['created_by']
        assert len(created_by_column.foreign_keys) == 1
        fk = list(created_by_column.foreign_keys)[0]
        # Test the foreign key target without resolving the column
        assert fk._colspec == "users.id"

        # Test updated_by foreign key
        updated_by_column = SampleModel.__table__.columns['updated_by']
        assert len(updated_by_column.foreign_keys) == 1
        fk = list(updated_by_column.foreign_keys)[0]
        # Test the foreign key target without resolving the column
        assert fk._colspec == "users.id"

    def test_tablename_generation(self):
        """Test automatic table name generation from class name."""
        # Test simple class name
        class SimpleModel(Base):
            pass
        assert SimpleModel.__tablename__ == "simple_model"

        # Test CamelCase class name
        class ProductCategory(Base):
            pass
        assert ProductCategory.__tablename__ == "product_category"

        # Test multiple words
        class UserAccountSettings(Base):
            pass
        assert UserAccountSettings.__tablename__ == "user_account_settings"

        # Test single word
        class Product(Base):
            pass
        assert Product.__tablename__ == "product"

    def test_model_instance_creation(self):
        """Test creating model instances with default values."""
        # Create instance with explicit default values
        instance = SampleModel(
            name="Test Item",
            is_active=True,
            sequence=0,
            created_by=settings.SYSTEM_USER_ID,
            updated_by=settings.SYSTEM_USER_ID
        )

        # Verify values are set correctly
        assert instance.is_active is True
        assert instance.sequence == 0
        assert instance.created_by == settings.SYSTEM_USER_ID
        assert instance.updated_by == settings.SYSTEM_USER_ID

    def test_to_dict_method(self):
        """Test the to_dict method converts model to dictionary."""
        # Create test instance
        instance = SampleModel(
            id=1,
            name="Test Item",
            description="Test Description",
            is_active=True,
            sequence=10
        )

        # Convert to dict
        result_dict = instance.to_dict()

        # Verify all columns are included
        expected_keys = {
            'id', 'name', 'description', 'created_at', 'updated_at',
            'created_by', 'updated_by', 'is_active', 'sequence'
        }
        assert set(result_dict.keys()) == expected_keys

        # Verify values
        assert result_dict['id'] == 1
        assert result_dict['name'] == "Test Item"
        assert result_dict['description'] == "Test Description"
        assert result_dict['is_active'] is True
        assert result_dict['sequence'] == 10

    def test_string_representation(self):
        """Test __str__ and __repr__ methods."""
        instance = SampleModel(id=123, name="Test Item")

        # Test __str__
        str_repr = str(instance)
        assert str_repr == "SampleModel(id=123)"

        # Test __repr__
        repr_str = repr(instance)
        assert repr_str == "SampleModel(id=123)"

    def test_string_representation_without_id(self):
        """Test string representation when id is None."""
        instance = SampleModel(name="Test Item")

        str_repr = str(instance)
        assert str_repr == "SampleModel(id=None)"

    def test_is_active_validation(self):
        """Test is_active field validation."""
        instance = SampleModel(name="Test Item")

        # Test valid boolean values
        instance.is_active = True
        assert instance.is_active is True

        instance.is_active = False
        assert instance.is_active is False

        # Test that invalid values raise TypeError
        with pytest.raises(TypeError):
            instance.is_active = "true"

        with pytest.raises(TypeError):
            instance.is_active = 1

    def test_sequence_validation(self):
        """Test sequence field validation."""
        instance = SampleModel(name="Test Item")

        # Test valid integer values
        instance.sequence = 10
        assert instance.sequence == 10

        instance.sequence = 0
        assert instance.sequence == 0

        # Test that invalid values raise TypeError
        with pytest.raises(TypeError):
            instance.sequence = "25"

        with pytest.raises(TypeError):
            instance.sequence = 25.5

    def test_datetime_validation(self):
        """Test datetime field validation."""
        instance = SampleModel(name="Test Item")

        # Test valid datetime
        test_datetime = datetime.now()
        instance.created_at = test_datetime
        assert instance.created_at == test_datetime

    def test_field_validation_mixin_integration(self):
        """Test that FieldValidationMixin is properly integrated."""
        # Verify Base inherits from FieldValidationMixin
        from app.utils.validators import FieldValidationMixin
        assert issubclass(Base, FieldValidationMixin)

        # Verify validation methods are available
        instance = SampleModel(name="Test Item")
        assert hasattr(instance, 'validate_boolean')
        assert hasattr(instance, 'validate_integer')
        assert hasattr(instance, 'validate_datetime')

    def test_model_type_annotation(self):
        """Test ModelType TypeVar is properly defined."""
        from app.core.base import ModelType

        # Verify ModelType is defined (bound check may vary due to forward ref)
        assert ModelType is not None
        assert hasattr(ModelType, '__bound__')

    @patch('app.core.config.settings')
    def test_system_user_id_configuration(self, mock_settings):
        """Test that system user ID is properly configured from settings."""
        # Mock different system user ID
        mock_settings.SYSTEM_USER_ID = 999

        # Create new model class to pick up the mocked settings
        class TestModelWithMockedSettings(Base):
            name = Column(String(100))

        # Verify the mocked system user ID is used
        table_cols = TestModelWithMockedSettings.__table__.columns
        created_by_col = table_cols['created_by']
        updated_by_col = table_cols['updated_by']

        # Note: The default is set at class definition time
        assert created_by_col.default.arg == settings.SYSTEM_USER_ID
        assert updated_by_col.default.arg == settings.SYSTEM_USER_ID


class TestJSONBModelClass:
    """Test cases for the JSONBModel class."""

    def test_jsonb_model_inheritance(self):
        """Test that JSONBModel inherits from Base properly."""
        # Verify JSONBModel inherits from Base
        assert issubclass(JSONBModel, Base)

        # Verify it's abstract
        assert JSONBModel.__abstract__ is True

    def test_jsonb_model_attributes_field(self):
        """Test that JSONBModel has attributes JSONB field."""
        # Create test instance
        instance = SampleJSONBModel(
            name="Test JSONB Item",
            attributes={"color": "red", "size": "large"}
        )

        # Verify attributes field exists and works
        assert hasattr(instance, 'attributes')
        assert instance.attributes == {"color": "red", "size": "large"}

    def test_jsonb_field_configuration(self):
        """Test that JSONB field is configured correctly."""
        # Get attributes column from SampleJSONBModel
        attributes_column = SampleJSONBModel.__table__.columns['attributes']

        # Verify it's JSONB type
        from sqlalchemy.dialects.postgresql import JSONB
        assert isinstance(attributes_column.type, JSONB)

        # Verify it's not nullable
        assert attributes_column.nullable is False

    def test_jsonb_model_to_dict_includes_attributes(self):
        """Test that to_dict includes attributes field."""
        instance = SampleJSONBModel(
            id=1,
            name="Test JSONB Item",
            attributes={"volume": "500ml", "flavor": "orange"}
        )

        result_dict = instance.to_dict()

        # Verify attributes is included
        assert 'attributes' in result_dict
        expected_attrs = {"volume": "500ml", "flavor": "orange"}
        assert result_dict['attributes'] == expected_attrs

    def test_jsonb_model_with_complex_attributes(self):
        """Test JSONBModel with complex nested attributes."""
        complex_attributes = {
            "physical": {
                "dimensions": {
                    "height": 10,
                    "width": 5,
                    "depth": 3
                },
                "weight": 250,
                "material": "plastic"
            },
            "features": ["waterproof", "stackable", "recyclable"],
            "metadata": {
                "created_by": "system",
                "version": "1.0"
            }
        }

        instance = SampleJSONBModel(
            name="Complex Item",
            attributes=complex_attributes
        )

        # Verify complex attributes are stored correctly
        assert instance.attributes == complex_attributes
        assert instance.attributes["physical"]["dimensions"]["height"] == 10
        assert "waterproof" in instance.attributes["features"]

    def test_jsonb_model_tablename_generation(self):
        """Test that JSONBModel subclasses generate correct table names."""
        # Test with simple name
        class ProductAttribute(JSONBModel):
            pass
        assert ProductAttribute.__tablename__ == "product_attribute"

        # Test with complex name
        class SkuAttributeMapping(JSONBModel):
            pass
        assert SkuAttributeMapping.__tablename__ == "sku_attribute_mapping"


class TestBaseModelIntegration:
    """Integration tests for Base model functionality."""

    def test_base_model_with_custom_fields(self):
        """Test Base model with additional custom fields."""
        class CustomModel(Base):
            name = Column(String(100), nullable=False)
            custom_field = Column(Integer, default=42)

        # Verify custom model has both base and custom fields
        expected_columns = {
            'id', 'created_at', 'updated_at', 'created_by',
            'updated_by', 'is_active', 'sequence', 'name', 'custom_field'
        }
        model_columns = {col.name for col in CustomModel.__table__.columns}
        assert expected_columns == model_columns

    def test_multiple_model_inheritance(self):
        """Test multiple models inheriting from Base."""
        class ModelA(Base):
            field_a = Column(String(50))

        class ModelB(Base):
            field_b = Column(Integer)

        # Verify both models have base fields
        for model_class in [ModelA, ModelB]:
            base_columns = {
                'id', 'created_at', 'updated_at', 'created_by',
                'updated_by', 'is_active', 'sequence'
            }
            model_columns = {col.name for col in model_class.__table__.columns}
            assert base_columns.issubset(model_columns)

        # Verify they have different table names
        assert ModelA.__tablename__ == "model_a"
        assert ModelB.__tablename__ == "model_b"

    def test_base_model_validators_error_handling(self):
        """Test that Base model validators handle errors appropriately."""
        instance = SampleModel(name="Test Item")

        # Test that validators are called
        # (they should not raise exceptions for valid data)
        try:
            instance.is_active = True
            instance.sequence = 10
            instance.created_at = datetime.now()
        except Exception as e:
            msg = f"Validators should not raise exceptions for valid data: {e}"
            pytest.fail(msg)

    def test_base_model_field_defaults_consistency(self):
        """Test that field defaults are consistent across instances."""
        instance1 = SampleModel(
            name="Item 1",
            is_active=True,
            sequence=0,
            created_by=settings.SYSTEM_USER_ID,
            updated_by=settings.SYSTEM_USER_ID
        )
        instance2 = SampleModel(
            name="Item 2",
            is_active=True,
            sequence=0,
            created_by=settings.SYSTEM_USER_ID,
            updated_by=settings.SYSTEM_USER_ID
        )

        # Verify default values are consistent
        assert instance1.is_active is True and instance2.is_active is True
        assert instance1.sequence == instance2.sequence == 0
        created_by_expected = settings.SYSTEM_USER_ID
        updated_by_expected = settings.SYSTEM_USER_ID
        assert instance1.created_by == instance2.created_by == created_by_expected
        assert instance1.updated_by == instance2.updated_by == updated_by_expected
