import pytest
from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError

from app.core.base import Base
from tests.utils.model_test_utils import save_object, get_all_objects, get_object_by_id


class SimpleTestModel(Base):
    """Simple model for testing common operations."""
    name = Column(String(50), nullable=False)


class TestCommonOperations:
    """Test common database operations including bulk operations."""

    async def test_bulk_creation_success(self, db_session: AsyncSession):
        """Test successful bulk creation of multiple objects."""
        # Arrange
        items = [
            SimpleTestModel(name="Item 1"),
            SimpleTestModel(name="Item 2"),
            SimpleTestModel(name="Item 3"),
            SimpleTestModel(name="Item 4"),
            SimpleTestModel(name="Item 5"),
        ]

        # Act
        db_session.add_all(items)
        await db_session.commit()

        # Assert - Check all items were created
        created_items = await get_all_objects(db_session, SimpleTestModel)

        assert len(created_items) == 5

        # Verify each item
        for i, item in enumerate(created_items, 1):
            assert item.id is not None
            assert item.name == f"Item {i}"

    async def test_bulk_creation_rollback_on_error(self, db_session: AsyncSession):
        """Test that bulk creation is rolled back when one item fails."""
        # Arrange - Create valid items and one invalid item
        valid_items = [
            SimpleTestModel(name="Valid Item 1"),
            SimpleTestModel(name="Valid Item 2"),
        ]

        # Invalid item with name that's too long (exceeds 50 chars)
        invalid_item = SimpleTestModel(
            name="This is a very long name that exceeds the maximum length "
                 "limit of 50 characters",
        )

        # Act & Assert
        db_session.add_all(valid_items)
        db_session.add(invalid_item)

        with pytest.raises(DBAPIError):
            await db_session.commit()

        await db_session.rollback()

        # Verify no items were created due to rollback
        items = await get_all_objects(db_session, SimpleTestModel)
        assert len(items) == 0

    async def test_bulk_creation_partial_commit(self, db_session: AsyncSession):
        """Test bulk creation with partial commit strategy."""
        # Arrange
        valid_items = [
            SimpleTestModel(name="Valid 1"),
            SimpleTestModel(name="Valid 2"),
            SimpleTestModel(name="Valid 3"),
        ]

        # Act - Add valid items first and commit
        db_session.add_all(valid_items)
        await db_session.commit()

        # Try to add invalid item separately
        invalid_item = SimpleTestModel(
            name="This name is way too long and will definitely exceed the "
                 "fifty character limit",
        )

        db_session.add(invalid_item)

        with pytest.raises(DBAPIError):
            await db_session.commit()

        await db_session.rollback()

        # Assert - Valid items should still exist
        items = await get_all_objects(db_session, SimpleTestModel)
        assert len(items) == 3

    async def test_bulk_creation_empty_list(self, db_session: AsyncSession):
        """Test bulk creation with empty list."""
        # Arrange
        items = []

        # Act
        db_session.add_all(items)
        await db_session.commit()

        # Assert
        created_items = await get_all_objects(db_session, SimpleTestModel)
        assert len(created_items) == 0

    async def test_bulk_creation_large_batch(self, db_session: AsyncSession):
        """Test bulk creation with a large number of items."""
        # Arrange
        batch_size = 100
        items = [
            SimpleTestModel(name=f"Batch Item {i}")
            for i in range(1, batch_size + 1)
        ]

        # Act
        db_session.add_all(items)
        await db_session.commit()

        # Assert
        created_items = await get_all_objects(db_session, SimpleTestModel)

        assert len(created_items) == batch_size

        # Verify first and last items
        first_item = next(
            item for item in created_items if item.name == "Batch Item 1"
        )
        last_item = next(
            item for item in created_items
            if item.name == f"Batch Item {batch_size}"
        )

        assert first_item.id == 1
        assert last_item.id == batch_size

    async def test_rollback_on_error(self, db_session: AsyncSession):
        """Test that a transaction is rolled back if an error occurs during bulk
        creation of models with valid and invalid values."""
        # Arrange
        item = SimpleTestModel(name="A"*100)
        with pytest.raises(DBAPIError):
            await save_object(db_session, item)

        await db_session.rollback()

        model = await get_object_by_id(db_session, SimpleTestModel, item.id)
        assert model is None

    async def test_data_not_updated_when_rollback(self, db_session: AsyncSession):
        """Test that data is not updated when rollback occurs."""
        # Arrange
        item = SimpleTestModel(name="test value")
        await save_object(db_session, item)
        item_id = item.id

        item.name = "test value 2"

        await db_session.rollback()

        result = await get_object_by_id(db_session, SimpleTestModel, item_id)
        assert result.name == "test value"

        result.name = "test value 3"
        await save_object(db_session, result)

        result = await get_object_by_id(db_session, SimpleTestModel, item_id)
        assert result.name == "test value 3"

    async def test_bulk_rollback_on_constraint_violation(
        self, db_session: AsyncSession
    ):
        """Test bulk rollback when constraint violation occurs in the middle."""
        # Arrange - Create some valid items first
        valid_items = [
            SimpleTestModel(name="Valid 1"),
            SimpleTestModel(name="Valid 2"),
        ]
        db_session.add_all(valid_items)
        await db_session.commit()

        # Create a mix of valid and invalid items for bulk operation
        bulk_items = [
            SimpleTestModel(name="Bulk Valid 1"),
            SimpleTestModel(name="Bulk Valid 2"),
            SimpleTestModel(name="A" * 100),  # This will fail - too long
            SimpleTestModel(name="Bulk Valid 3"),  # This won't be saved due to rollback
        ]

        # Act & Assert
        db_session.add_all(bulk_items)
        with pytest.raises(DBAPIError):
            await db_session.commit()

        await db_session.rollback()

        # Verify only the initial valid items exist
        all_items = await get_all_objects(db_session, SimpleTestModel)
        assert len(all_items) == 2
        assert all(item.name in ["Valid 1", "Valid 2"] for item in all_items)

    async def test_multiple_rollbacks_in_sequence(self, db_session: AsyncSession):
        """Test multiple rollback operations in sequence."""
        # First failed transaction
        item1 = SimpleTestModel(name="C" * 100)  # Too long
        db_session.add(item1)
        with pytest.raises(DBAPIError):
            await db_session.commit()
        await db_session.rollback()

        # Second failed transaction
        item2 = SimpleTestModel(name="D" * 100)  # Too long
        db_session.add(item2)
        with pytest.raises(DBAPIError):
            await db_session.commit()
        await db_session.rollback()

        # Third successful transaction
        item3 = SimpleTestModel(name="Valid Item")
        await save_object(db_session, item3)

        # Verify only the valid item exists
        all_items = await get_all_objects(db_session, SimpleTestModel)
        assert len(all_items) == 1
        assert all_items[0].name == "Valid Item"

    async def test_rollback_with_foreign_key_constraint(self, db_session: AsyncSession):
        """Test rollback when foreign key constraint is violated."""
        # Arrange - Create an item with invalid foreign key reference
        # This assumes created_by references users.id
        item = SimpleTestModel(name="FK Test")
        item.created_by = 99999  # Non-existent user ID

        # Act & Assert
        db_session.add(item)
        with pytest.raises(DBAPIError):
            await db_session.commit()

        await db_session.rollback()

        # Verify no items were created
        all_items = await get_all_objects(db_session, SimpleTestModel)
        assert len(all_items) == 0

    async def test_rollback_preserves_session_state(self, db_session: AsyncSession):
        """Test that rollback preserves session state correctly."""
        # Arrange - Create a valid item first
        valid_item = SimpleTestModel(name="Session State Test")
        await save_object(db_session, valid_item)

        valid_item_id = valid_item.id

        # Modify the item in memory
        valid_item.name = "Modified Name"

        # Add an invalid item to force rollback
        invalid_item = SimpleTestModel(name="E" * 100)
        db_session.add(invalid_item)

        # Act & Assert
        with pytest.raises(DBAPIError):
            await db_session.commit()

        await db_session.rollback()

        # Verify the item in database still has original name
        db_item = await get_object_by_id(db_session, SimpleTestModel, valid_item_id)
        assert db_item.name == "Session State Test"

        # Verify the in-memory object state after rollback
        await db_session.refresh(valid_item)
        assert valid_item.name == "Session State Test"

    async def test_rollback_with_flush_before_commit(self, db_session: AsyncSession):
        """Test rollback behavior when flush is called before commit."""
        # Arrange
        items = [
            SimpleTestModel(name="Flush Test 1"),
            SimpleTestModel(name="Flush Test 2"),
            SimpleTestModel(name="F" * 100),  # This will fail
        ]

        # Act
        db_session.add_all(items)

        # Flush should fail before commit
        with pytest.raises(DBAPIError):
            await db_session.flush()

        await db_session.rollback()

        # Assert
        all_items = await get_all_objects(db_session, SimpleTestModel)
        assert len(all_items) == 0
