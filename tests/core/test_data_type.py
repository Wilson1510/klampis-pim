from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.future import select
from sqlalchemy.exc import DBAPIError, StatementError
import pytest

from app.core.base import Base


class SampleModelDataType(Base):
    """Sample model for testing data type."""
    sample_integer = Column(Integer)
    sample_string = Column(String)
    sample_boolean = Column(Boolean)
    sample_float = Column(Float)
    sample_datetime = Column(DateTime(timezone=True))
    sample_jsonb = Column(JSONB)
    sample_text = Column(Text)


class TestDataType:
    async def create_item(self, valid_data, invalid_data, target_field, session):
        for data in valid_data:
            sample = SampleModelDataType(**{target_field: data})
            session.add(sample)
            await session.commit()

        for data, error_type, error_message in invalid_data:
            sample = SampleModelDataType(**{target_field: data})
            session.add(sample)

            with pytest.raises(error_type, match=error_message):
                await session.commit()
            await session.rollback()

    async def test_string_field_validation(self, db_session):
        valid_data = ["test", "test with spaces", "  test with whitespace   ", ("test")]
        invalid_data = [
            # [data, error_type, error_message]
            [123, DBAPIError, "expected str, got int"],
            [12.3, DBAPIError, "expected str, got float"],
            [True, DBAPIError, "expected str, got bool"],
            [['test'], DBAPIError, "expected str, got list"],
            [['test1', 'test2'], DBAPIError, "expected str, got list"],
            [[], DBAPIError, "expected str, got list"],
            [{'test1', 'test2'}, DBAPIError, "expected str, got set"],
            [{'test'}, DBAPIError, "expected str, got set"],
            [{'test key': 'test value'}, DBAPIError, "expected str, got dict"],
            [{}, DBAPIError, "expected str, got dict"],
            [('test1', 'test2'), DBAPIError, "expected str, got tuple"],
            [(), DBAPIError, "expected str, got tuple"],
            [datetime.now(), DBAPIError, "expected str, got datetime"]
        ]

        await self.create_item(valid_data, invalid_data, "sample_string", db_session)

    async def test_integer_field_validation(self, db_session):
        valid_data = [-99999, 0, 00, 99999, (88)]
        invalid_data = [
            ["test", DBAPIError, "'str' object cannot be interpreted as an integer"],
            [2147483648, DBAPIError, "value out of int32 range"],
            [-2147483649, DBAPIError, "value out of int32 range"],
            [
                999.00,
                TypeError,
                "Column 'sample_integer' must be an integer, not a float."
            ],
            [
                999.99,
                TypeError,
                "Column 'sample_integer' must be an integer, not a float."
            ],
            [
                False,
                TypeError,
                "Column 'sample_integer' must be an integer, not a boolean."
            ],
            ["999", DBAPIError, "'str' object cannot be interpreted as an integer"],
            [[999], DBAPIError, "'list' object cannot be interpreted as an integer"],
            [
                [998, 999],
                DBAPIError,
                "'list' object cannot be interpreted as an integer"
            ],
            [[], DBAPIError, "'list' object cannot be interpreted as an integer"],
            [{999}, DBAPIError, "'set' object cannot be interpreted as an integer"],
            [
                {998, 999},
                DBAPIError,
                "'set' object cannot be interpreted as an integer"
            ],
            [
                {998: 999},
                DBAPIError,
                "'dict' object cannot be interpreted as an integer"
            ],
            [{}, DBAPIError, "'dict' object cannot be interpreted as an integer"],
            [
                (998, 999),
                DBAPIError,
                "'tuple' object cannot be interpreted as an integer"
            ],
            [(), DBAPIError, "'tuple' object cannot be interpreted as an integer"],
            [
                datetime.now(),
                DBAPIError,
                "'datetime.datetime' object cannot be interpreted as an integer"
            ]
        ]

        await self.create_item(valid_data, invalid_data, "sample_integer", db_session)

    async def test_boolean_field_validation(self, db_session):
        valid_data = [True, False, (True)]
        invalid_data = [
            ["true", StatementError, "Not a boolean value: 'true'"],
            ["false", StatementError, "Not a boolean value: 'false'"],
            ["test", StatementError, "Not a boolean value: 'test'"],
            ["yes", StatementError, "Not a boolean value: 'yes'"],
            ["no", StatementError, "Not a boolean value: 'no'"],
            [1, TypeError, "Column 'sample_boolean' must be a boolean, not int."],
            [0, TypeError, "Column 'sample_boolean' must be a boolean, not int."],
            [2, StatementError, "Value 2 is not None, True, or False"],
            [999, StatementError, "Value 999 is not None, True, or False"],
            [1.0, TypeError, "Column 'sample_boolean' must be a boolean, not float."],
            [0.0, TypeError, "Column 'sample_boolean' must be a boolean, not float."],
            [9.99, StatementError, "Not a boolean value: 9.99"],
            [[False], StatementError, "unhashable type: 'list'"],
            [[True, False], StatementError, "unhashable type: 'list'"],
            [[], StatementError, "unhashable type: 'list'"],
            [{True}, StatementError, "Not a boolean value: {True}"],
            [{False, True}, StatementError, "Not a boolean value: {False, True}"],
            [{True: True}, StatementError, "unhashable type: 'dict'"],
            [{}, StatementError, "unhashable type: 'dict'"],
            [
                datetime(2025, 6, 8, 18, 19, 37, 718543),
                StatementError,
                "Not a boolean value: datetime\\.datetime\\("
                "2025, 6, 8, 18, 19, 37, 718543\\)"
            ],
            [(True, False), StatementError, "Not a boolean value: \\(True, False\\)"],
            [(), StatementError, "Not a boolean value: \\(\\)"]
        ]

        await self.create_item(valid_data, invalid_data, "sample_boolean", db_session)

    # async def test_create_item2(self, db_session):
    #     sample = SampleModelDataType(
    #         sample_string="test",
    #         sample_integer=00,
    #         sample_boolean=False,
    #         sample_float=123.45,
    #         sample_datetime="2025-06-02 23:20:35.661597+0419",
    #         sample_jsonb=('test1', 'test2'),
    #         sample_text=" 25 "
    #     )
    #     print(f"Create Item: {sample.sample_integer}, "
    #           f"type: {type(sample.sample_integer)}")

    #     db_session.add(sample)
    #     await db_session.commit()

    #     query = select(SampleModelDataType).where(
    #         SampleModelDataType.sample_string == "test"
    #     )
    #     stmt = await db_session.execute(query)
    #     item = stmt.scalars().first()
    #     print(f"Create Item: {item.sample_integer}, "
    #           f"type: {type(item.sample_integer)}")
