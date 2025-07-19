from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from tests.utils.model_test_utils import save_object


class SampleModelRealConstraint(Base):
    """Sample model for testing real constraints."""
    # String with multiple constraints + index
    constraint_string = Column(String(20), unique=True, nullable=False, index=True)

    # Simple string without constraints
    simple_string = Column(String(100))

    # Foreign key with index
    fk_field = Column(Integer, ForeignKey("users.id"), index=True)

    # Field with only index (no other constraints)
    indexed_field = Column(String(50), index=True)


class TestConstraintBehavior:
    """Test constraint behavior at database level."""

    async def test_unique_constraint(self, db_session: AsyncSession):
        """Test unique constraint prevents duplicate values."""
        # Create first record
        obj1 = SampleModelRealConstraint(constraint_string="unique_value")
        await save_object(db_session, obj1)

        # Try to create duplicate
        obj2 = SampleModelRealConstraint(constraint_string="unique_value")

        with pytest.raises(DBAPIError):
            await save_object(db_session, obj2)
        await db_session.rollback()

    async def test_not_null_constraint(self, db_session: AsyncSession):
        """Test not null constraint prevents null values."""
        # Try to create record with null value for not-null field
        obj = SampleModelRealConstraint(constraint_string=None)

        with pytest.raises(DBAPIError):
            await save_object(db_session, obj)
        await db_session.rollback()

        obj = SampleModelRealConstraint(constraint_string="")
        with pytest.raises(ValueError):
            await save_object(db_session, obj)
        await db_session.rollback()

    async def test_foreign_key_constraint(self, db_session: AsyncSession):
        """Test foreign key constraint prevents invalid references."""
        # Try to create record with invalid foreign key
        obj = SampleModelRealConstraint(
            constraint_string="valid_string",
            fk_field=99999  # Non-existent user ID
        )

        with pytest.raises(DBAPIError):
            await save_object(db_session, obj)
        await db_session.rollback()

    async def test_string_length_constraint(self, db_session: AsyncSession):
        """Test string length constraint behavior."""
        # Test valid length (exactly 20 chars)
        valid_obj = SampleModelRealConstraint(constraint_string="A" * 20)
        await save_object(db_session, valid_obj)

        # Test invalid length (21 chars)
        invalid_obj = SampleModelRealConstraint(constraint_string="A" * 21)
        with pytest.raises(DBAPIError):
            await save_object(db_session, invalid_obj)

        await db_session.rollback()


class TestIndexBehavior:
    """Test index behavior (limited testing since indexes are for performance)."""

    def test_index_exists_in_database_metadata(self):
        """Test that indexes exist in database metadata."""
        # This is more of a configuration test, but validates index creation
        table = SampleModelRealConstraint.__table__

        # Check that indexed columns are marked as indexed
        indexed_columns = [
            col for col in table.columns
            if col.index is True
        ]

        assert len(indexed_columns) >= 3  # constraint_string, fk_field, indexed_field

        # Note: Testing actual index performance would require integration tests
        # with real data and query execution plans
