from datetime import datetime
from unittest.mock import patch

from sqlalchemy import Column, String, Integer, Text

from app.core.base import Base
from app.core.config import settings


# Test model untuk testing Base functionality
class SampleModelBase(Base):
    """Sample model for Base functionality testing."""
    name = Column(String(100), nullable=False)
    description = Column(Text)


class TestBaseModel:
    """Test cases for the Base model class."""

    def test_base_model_inheritance(self):
        """Test that Base model can be inherited properly."""
        # Verify SampleModel inherits from Base
        assert issubclass(SampleModelBase, Base)

        # Verify SampleModel has all expected columns
        expected_columns = {
            'id', 'created_at', 'updated_at', 'created_by',
            'updated_by', 'is_active', 'sequence'
        }
        model_columns = {col.name for col in SampleModelBase.__table__.columns}
        assert expected_columns.issubset(model_columns)
        assert len(model_columns) == 9
        assert 'invalid_column' not in model_columns

        assert hasattr(SampleModelBase, '__tablename__')
        assert hasattr(SampleModelBase, 'to_dict')

    def test_base_model_fields_configuration(self):
        """Test that Base model fields are configured correctly."""
        # Test id field
        id_column = SampleModelBase.__table__.columns['id']
        assert id_column.primary_key is True
        assert id_column.autoincrement is True
        assert id_column.type.python_type == int

        # Test created_at field
        created_at_column = SampleModelBase.__table__.columns['created_at']
        assert created_at_column.nullable is False
        assert created_at_column.server_default is not None
        assert created_at_column.type.python_type == datetime

        # Test updated_at field
        updated_at_column = SampleModelBase.__table__.columns['updated_at']
        assert updated_at_column.nullable is False
        assert updated_at_column.server_default is not None
        assert updated_at_column.onupdate is not None
        assert updated_at_column.type.python_type == datetime

        # Test created_by field
        created_by_column = SampleModelBase.__table__.columns['created_by']
        assert created_by_column.nullable is False
        assert created_by_column.default.arg == settings.SYSTEM_USER_ID
        assert created_by_column.type.python_type == int
        assert len(created_by_column.foreign_keys) == 1
        foreign_key = list(created_by_column.foreign_keys)[0]
        assert foreign_key._colspec == "users.id"

        # Test updated_by field
        updated_by_column = SampleModelBase.__table__.columns['updated_by']
        assert updated_by_column.nullable is False
        assert updated_by_column.default.arg == settings.SYSTEM_USER_ID
        assert updated_by_column.type.python_type == int
        assert len(updated_by_column.foreign_keys) == 1
        foreign_key = list(updated_by_column.foreign_keys)[0]
        assert foreign_key._colspec == "users.id"

        # Test is_active field
        is_active_column = SampleModelBase.__table__.columns['is_active']
        assert is_active_column.nullable is False
        assert is_active_column.default.arg is True
        assert is_active_column.type.python_type == bool

        # Test sequence field
        sequence_column = SampleModelBase.__table__.columns['sequence']
        assert sequence_column.nullable is False
        assert sequence_column.default.arg == 0
        assert sequence_column.type.python_type == int

    def test_tablename_generation(self):
        """Test automatic table name generation from class name."""
        # Test simple class name
        class SimpleModel(Base):
            pass
        assert SimpleModel.__tablename__ == "simple_model"

        # Test multiple words
        class UserAccountSettings(Base):
            pass
        assert UserAccountSettings.__tablename__ == "user_account_settings"

        # Test single word
        class Product(Base):
            pass
        assert Product.__tablename__ == "product"

    def test_model_instantiation(self):
        """Test model instantiation."""
        instance = SampleModelBase(name="Test Item")

        # Every default value should be None because it will be set when the
        # instance is saved to the database
        assert instance.id is None
        assert instance.name == "Test Item"
        assert instance.description is None
        assert instance.created_at is None
        assert instance.updated_at is None
        assert instance.created_by is None
        assert instance.updated_by is None
        assert instance.is_active is None
        assert instance.sequence is None

        assert isinstance(instance, SampleModelBase)
        assert isinstance(instance, Base)

        assert hasattr(instance, '__tablename__')
        assert hasattr(instance, 'to_dict')

    def test_to_dict_method(self):
        """Test the to_dict method converts model to dictionary."""
        # Create test instance
        instance = SampleModelBase(
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
        assert result_dict['created_at'] is None
        assert result_dict['updated_at'] is None
        assert result_dict['created_by'] is None
        assert result_dict['updated_by'] is None

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

    async def test_model_instance_creation(self, db_session):
        """Test creating model instances with default values."""
        # Create instance with explicit default values
        default_instance = SampleModelBase(name="Test Item")
        db_session.add(default_instance)
        await db_session.commit()

        # Verify values are set correctly
        assert default_instance.id == 1
        assert default_instance.name == "Test Item"
        assert default_instance.description is None
        assert default_instance.created_at is not None
        assert default_instance.updated_at is not None
        assert default_instance.created_at == default_instance.updated_at
        assert default_instance.created_by == settings.SYSTEM_USER_ID
        assert default_instance.updated_by == settings.SYSTEM_USER_ID
        assert default_instance.is_active is True
        assert default_instance.sequence == 0

        # Create instance with explicit values
        explicit_instance = SampleModelBase(
            id=2,
            name="Explicit Item",
            description="Explicit Description",
            is_active=False,
            sequence=10,
            created_by=settings.SYSTEM_USER_ID,
            updated_by=settings.SYSTEM_USER_ID,
            created_at="2025-01-03 15:23:10",
            updated_at="2025-01-04 15:23:10"
        )
        db_session.add(explicit_instance)
        await db_session.commit()

        # Verify values are set correctly
        assert explicit_instance.id == 2
        assert explicit_instance.name == "Explicit Item"
        assert explicit_instance.description == "Explicit Description"
        assert explicit_instance.is_active is False
        assert explicit_instance.sequence == 10
        assert explicit_instance.created_by == settings.SYSTEM_USER_ID
        assert explicit_instance.updated_by == settings.SYSTEM_USER_ID
        assert explicit_instance.created_at == datetime(2025, 1, 3, 15, 23, 10)
        assert explicit_instance.updated_at == datetime(2025, 1, 4, 15, 23, 10)

    async def test_string_representation(self, db_session):
        """Test __str__ and __repr__ methods."""
        # with id and saved to the database
        instance = SampleModelBase(id=123, name="Test Item")
        db_session.add(instance)
        await db_session.commit()

        # Test __str__
        str_repr = str(instance)
        assert str_repr == "SampleModelBase(id=123)"

        # Test __repr__
        repr_str = repr(instance)
        assert repr_str == "SampleModelBase(id=123)"

        # without id and saved to the database
        instance = SampleModelBase(name="Test Item 1")
        db_session.add(instance)
        await db_session.commit()  # save the instance to the database

        # Test __str__
        str_repr = str(instance)
        assert str_repr == "SampleModelBase(id=1)"

        # Test __repr__
        repr_str = repr(instance)
        assert repr_str == "SampleModelBase(id=1)"

        # with id and not saved to the database
        instance = SampleModelBase(id=2, name="Test Item 2")
        db_session.add(instance)
        await db_session.commit()

        # Test __str__
        str_repr = str(instance)
        assert str_repr == "SampleModelBase(id=2)"

        # Test __repr__
        repr_str = repr(instance)
        assert repr_str == "SampleModelBase(id=2)"

        # without id and not saved to the database
        instance = SampleModelBase(name="Test Item 3")
        str_repr = str(instance)
        assert str_repr == "SampleModelBase(id=None)"

        repr_str = repr(instance)
        assert repr_str == "SampleModelBase(id=None)"
