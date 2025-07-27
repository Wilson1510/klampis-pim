from sqlalchemy import Column, String, Integer, ForeignKey, Float, Numeric, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from tests.utils.model_test_utils import save_object


class ModelRealConstraint(Base):
    """Sample model for testing real constraints."""
    # String with multiple constraints + index
    constraint_string = Column(String(20), unique=True, nullable=False, index=True)

    # Simple string without constraints
    simple_string = Column(String(100))

    # Foreign key with index
    fk_field = Column(Integer, ForeignKey("users.id"), index=True)

    # Field with only index (no other constraints)
    indexed_field = Column(String(50), index=True)


class ModelCustomConstraint(Base):
    """Sample model for testing custom constraints."""
    test_email = Column(String(50))
    emailtest = Column(String(50))
    testemailtest = Column(String(50))

    testphone = Column(String(50))
    phone_test = Column(String(50))
    test_phone_test = Column(String(50))

    test_quantity = Column(Float)
    quantity_test = Column(Float)
    test_quantity_test = Column(Numeric(10, 2))

    test_sequence = Column(Float)
    sequence_test = Column(Float)
    test_sequence_test = Column(Float)


class TestRealConstraint:
    """Test constraint behavior at database level."""

    async def test_unique_constraint(self, db_session: AsyncSession):
        """Test unique constraint prevents duplicate values."""
        # Create first record
        obj1 = ModelRealConstraint(constraint_string="unique_value")
        await save_object(db_session, obj1)

        # Try to create duplicate
        obj2 = ModelRealConstraint(constraint_string="unique_value")

        with pytest.raises(DBAPIError):
            await save_object(db_session, obj2)
        await db_session.rollback()

    async def test_not_null_constraint(self, db_session: AsyncSession):
        """Test not null constraint prevents null values."""
        # Try to create record with null value for not-null field
        obj = ModelRealConstraint(constraint_string=None)

        with pytest.raises(DBAPIError):
            await save_object(db_session, obj)
        await db_session.rollback()

        obj = ModelRealConstraint(constraint_string="")
        with pytest.raises(ValueError):
            await save_object(db_session, obj)
        await db_session.rollback()

    async def test_foreign_key_constraint(self, db_session: AsyncSession):
        """Test foreign key constraint prevents invalid references."""
        # Try to create record with invalid foreign key
        obj = ModelRealConstraint(
            constraint_string="valid_string",
            fk_field=99999  # Non-existent user ID
        )

        with pytest.raises(DBAPIError):
            await save_object(db_session, obj)
        await db_session.rollback()

    async def test_string_length_constraint(self, db_session: AsyncSession):
        """Test string length constraint behavior."""
        # Test valid length (exactly 20 chars)
        valid_obj = ModelRealConstraint(constraint_string="A" * 20)
        await save_object(db_session, valid_obj)

        # Test invalid length (21 chars)
        invalid_obj = ModelRealConstraint(constraint_string="A" * 21)
        with pytest.raises(DBAPIError):
            await save_object(db_session, invalid_obj)

        await db_session.rollback()


class TestIndexBehavior:
    """Test index behavior (limited testing since indexes are for performance)."""

    def test_index_exists_in_database_metadata(self):
        """Test that indexes exist in database metadata."""
        # This is more of a configuration test, but validates index creation
        table = ModelRealConstraint.__table__

        # Check that indexed columns are marked as indexed
        indexed_columns = [
            col for col in table.columns
            if col.index is True
        ]

        assert len(indexed_columns) >= 3  # constraint_string, fk_field, indexed_field

        # Note: Testing actual index performance would require integration tests
        # with real data and query execution plans


class TestCustomConstraintApplication:
    """Test custom constraint application."""

    async def create_item(self, valid_data, invalid_data, target_field, session):
        for data in valid_data:
            sample = ModelCustomConstraint(**{target_field: data})
            await save_object(session, sample)

        for data, error_type, error_message in invalid_data:
            sample = ModelCustomConstraint(**{target_field: data})
            with pytest.raises(error_type, match=error_message):
                await save_object(session, sample)
            await session.rollback()

    async def test_email_field_validation(self, db_session):
        columns = ModelCustomConstraint.__table__.columns
        email_columns = [
            column.name for column in columns
            if 'email' in column.name
        ]

        for email_column in email_columns:
            valid_data = ["test@gmail.com", "t@b", "email@m"]
            invalid_data = [
                # [data, error_type, error_message]
                ["test", ValueError, f"Column '{email_column}' must contain '@'."],
                [
                    "@gmail.com",
                    ValueError,
                    f"Column '{email_column}' must not start or end with '@'"
                ],
                [
                    "gmail.com@",
                    ValueError,
                    f"Column '{email_column}' must not start or end with '@'"
                ],
            ]

            await self.create_item(valid_data, invalid_data, email_column, db_session)

    async def test_phone_field_validation(self, db_session):
        columns = ModelCustomConstraint.__table__.columns
        phone_columns = [
            column.name for column in columns
            if 'phone' in column.name
        ]
        for phone_column in phone_columns:
            valid_data = ["081234567890", "08123456789", "41"]
            invalid_data = [
                # [data, error_type, error_message]
                [
                    "a82192034111",
                    ValueError,
                    f"Column '{phone_column}' must contain only digits."
                ],
                [
                    "08123 5678901",
                    ValueError,
                    f"Column '{phone_column}' must contain only digits."
                ],
                [
                    "0812-4562-1235",
                    ValueError,
                    f"Column '{phone_column}' must contain only digits."
                ],
                [
                    "+6281234567890",
                    ValueError,
                    f"Column '{phone_column}' must contain only digits."
                ]
            ]

            await self.create_item(valid_data, invalid_data, phone_column, db_session)

    async def test_quantity_field_validation(self, db_session):
        columns = ModelCustomConstraint.__table__.columns
        quantity_columns = [
            column.name for column in columns
            if 'quantity' in column.name
        ]
        for quantity_column in quantity_columns:
            valid_data = [52, 41.856, 0.01, 10e6, 10e-3]
            invalid_data = [
                # [data, error_type, error_message]
                [
                    -10e-6,
                    ValueError,
                    f"Column '{quantity_column}' must be a positive number."
                ],
                [
                    0,
                    ValueError,
                    f"Column '{quantity_column}' must be a positive number."
                ],
                [
                    -51,
                    ValueError,
                    f"Column '{quantity_column}' must be a positive number."
                ],
            ]

            await self.create_item(
                valid_data, invalid_data, quantity_column, db_session
            )

    async def test_sequence_field_validation(self, db_session):
        columns = ModelCustomConstraint.__table__.columns
        sequence_columns = [
            column.name for column in columns
            if 'sequence' in column.name and column.name != 'sequence'
        ]
        for sequence_column in sequence_columns:
            valid_data = [52, 41.856, 0.01, 0, 10e6, 10e-3]
            invalid_data = [
                # [data, error_type, error_message]
                [
                    -10e-6,
                    ValueError,
                    f"Column '{sequence_column}' must be a non-negative number."
                ],
                [
                    -0.01,
                    ValueError,
                    f"Column '{sequence_column}' must be a non-negative number."
                ],
                [
                    -51,
                    ValueError,
                    f"Column '{sequence_column}' must be a non-negative number."
                ],
            ]

            await self.create_item(
                valid_data, invalid_data, sequence_column, db_session
            )


class TestCustomConstraintDatabase:
    """Test custom constraint database."""

    async def create_item(self, valid_data, invalid_data, target_field, session):
        for data in valid_data:
            sql = text(f"""
                INSERT INTO model_custom_constraint (
                        {target_field},
                        is_active,
                        sequence,
                        created_by,
                        updated_by
                )
                VALUES (
                        :{target_field},
                        :is_active,
                        :sequence,
                        :created_by,
                        :updated_by
                )
            """)
            await session.execute(sql, {
                target_field: data,
                'is_active': True,
                'sequence': 1,
                'created_by': 1,
                'updated_by': 1
            })
            await session.commit()

        for data, error_type, error_message in invalid_data:
            sql = text(f"""
                INSERT INTO model_custom_constraint (
                        {target_field},
                        is_active,
                        sequence,
                        created_by,
                        updated_by
                )
                VALUES (
                        :{target_field},
                        :is_active,
                        :sequence,
                        :created_by,
                        :updated_by
                )
            """)
            with pytest.raises(error_type, match=error_message):
                await session.execute(sql, {
                    target_field: data,
                    'is_active': True,
                    'sequence': 1,
                    'created_by': 1,
                    'updated_by': 1
                })
            await session.rollback()

    async def test_email_field_validation(self, db_session):
        columns = ModelCustomConstraint.__table__.columns
        email_columns = [
            column.name for column in columns
            if 'email' in column.name
        ]

        for email_column in email_columns:
            valid_data = ["test@gmail.com", "t@b", "email@m"]
            invalid_data = [
                # [data, error_type, error_message]
                [
                    "test",
                    IntegrityError,
                    f"check_model_custom_constraint_{email_column}_format"
                ],
                [
                    "@gmail.com",
                    IntegrityError,
                    f"check_model_custom_constraint_{email_column}_format"
                ],
                [
                    "gmail.com@",
                    IntegrityError,
                    f"check_model_custom_constraint_{email_column}_format"
                ],
            ]

            await self.create_item(valid_data, invalid_data, email_column, db_session)

    async def test_phone_field_validation(self, db_session):
        columns = ModelCustomConstraint.__table__.columns
        phone_columns = [
            column.name for column in columns
            if 'phone' in column.name
        ]
        for phone_column in phone_columns:
            valid_data = ["081234567890", "08123456789", "41"]
            invalid_data = [
                # [data, error_type, error_message]
                [
                    "a82192034111",
                    IntegrityError,
                    f"check_model_custom_constraint_{phone_column}_digits_only"
                ],
                [
                    "08123 5678901",
                    IntegrityError,
                    f"check_model_custom_constraint_{phone_column}_digits_only"
                ],
                [
                    "0812-4562-1235",
                    IntegrityError,
                    f"check_model_custom_constraint_{phone_column}_digits_only"
                ],
                [
                    "+6281234567890",
                    IntegrityError,
                    f"check_model_custom_constraint_{phone_column}_digits_only"
                ]
            ]

            await self.create_item(valid_data, invalid_data, phone_column, db_session)

    async def test_quantity_field_validation(self, db_session):
        columns = ModelCustomConstraint.__table__.columns
        quantity_columns = [
            column.name for column in columns
            if 'quantity' in column.name
        ]
        for quantity_column in quantity_columns:
            valid_data = [52, 41.856, 0.01, 10e6, 10e-3]
            invalid_data = [
                # [data, error_type, error_message]
                [
                    -10e-6,
                    IntegrityError,
                    f"check_model_custom_constraint_{quantity_column}_positive"
                ],
                [
                    0,
                    IntegrityError,
                    f"check_model_custom_constraint_{quantity_column}_positive"
                ],
                [
                    -51,
                    IntegrityError,
                    f"check_model_custom_constraint_{quantity_column}_positive"
                ],
            ]

            await self.create_item(
                valid_data, invalid_data, quantity_column, db_session
            )

    async def test_sequence_field_validation(self, db_session):
        columns = ModelCustomConstraint.__table__.columns
        sequence_columns = [
            column.name for column in columns
            if 'sequence' in column.name and column.name != 'sequence'
        ]
        for sequence_column in sequence_columns:
            valid_data = [52, 41.856, 0.01, 0, 10e6, 10e-3]
            invalid_data = [
                # [data, error_type, error_message]
                [
                    -10e-6,
                    IntegrityError,
                    f"check_model_custom_constraint_{sequence_column}_non_negative"
                ],
                [
                    -0.01,
                    IntegrityError,
                    f"check_model_custom_constraint_{sequence_column}_non_negative"
                ],
                [
                    -51,
                    IntegrityError,
                    f"check_model_custom_constraint_{sequence_column}_non_negative"
                ],
            ]

            await self.create_item(
                valid_data, invalid_data, sequence_column, db_session
            )
