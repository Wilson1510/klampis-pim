import enum
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Boolean, Float, DateTime, Text, Enum, Numeric
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import DBAPIError, StatementError
import pytest

from app.core.base import Base


class SampleEnum(str, enum.Enum):
    FIRST = "FIRST"
    SECOND = "SECOND"
    THIRD = "THIRD"


class SampleModelDataType(Base):
    """Sample model for testing data type."""
    sample_integer = Column(Integer)
    sample_string = Column(String)
    sample_boolean = Column(Boolean)
    sample_float = Column(Float)
    sample_numeric = Column(Numeric(15, 2))
    sample_datetime = Column(DateTime(timezone=True))
    sample_jsonb = Column(JSONB)
    sample_text = Column(Text)
    sample_enum = Column(Enum(SampleEnum))


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
        valid_data = [
            "test", "test with spaces", "  test with whitespace   ", ("test"), "",
            "    "
        ]
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
            [datetime.now(), DBAPIError, "expected str, got datetime"],
            ["1test", ValueError, "Column 'sample_string' must start with a letter."],
            [
                'test*',
                ValueError,
                "Column 'sample_string' can only contain "
                "alphabet letters, numbers, underscores, and spaces."
            ],
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

    async def test_float_field_validation(self, db_session):
        valid_data = [-99999999999.99, 88.14, 2025, 99999999999.99, (88.0)]
        invalid_data = [
            [
                False,
                TypeError,
                "Column 'sample_float' must be a float or numeric, not a boolean."
            ],
            ["9999.99", DBAPIError, "(must be real number, not str)"],
            ["9999", DBAPIError, "(must be real number, not str)"],
            [[9999.99], DBAPIError, "(must be real number, not list)"],
            [[9999, 9999, 9999], DBAPIError, "(must be real number, not list)"],
            [[], DBAPIError, "(must be real number, not list)"],
            [{9999.99}, DBAPIError, "(must be real number, not set)"],
            [{9999.99, 9999.99}, DBAPIError, "(must be real number, not set)"],
            [{9999.99: 9999.99}, DBAPIError, "(must be real number, not dict)"],
            [{}, DBAPIError, "(must be real number, not dict)"],
            [(9999.99, 9999.99), DBAPIError, "(must be real number, not tuple)"],
            [(), DBAPIError, "(must be real number, not tuple)"],
            [
                datetime(2025, 6, 8, 18, 19, 37, 718543),
                DBAPIError,
                "(must be real number, not datetime.datetime)"
            ]
        ]

        await self.create_item(valid_data, invalid_data, "sample_float", db_session)

    async def test_numeric_field_validation(self, db_session):
        valid_data = [
            8887776665554.44, 77777.4, 77777.444, 8887776665554, 888777666555.4,
            2067, "3174.12", "1556", (77777.55)
        ]
        invalid_data = [
            [888777666555444, DBAPIError, "field numerik melebihi jangkauan"],
            [8887776665554443, DBAPIError, "field numerik melebihi jangkauan"],
            [888777666555444.2, DBAPIError, "field numerik melebihi jangkauan"],
            ["test123", DBAPIError, "class 'decimal.ConversionSyntax'"],
            [
                False,
                TypeError,
                "Column 'sample_numeric' must be a float or numeric, not a boolean."
            ],
            [[5732.21], DBAPIError, "argument must be a sequence of length 3"],
            [
                [3306.12, 5432, 12],
                DBAPIError,
                "(sign must be an integer with the value 0 or 1)"
            ],
            [[], DBAPIError, "(argument must be a sequence of length 3)"],
            [
                {1589.744},
                DBAPIError,
                "(conversion from set to Decimal is not supported)"
            ],
            [
                {2912.74, 1830.45},
                DBAPIError,
                "(conversion from set to Decimal is not supported)"
            ],
            [
                {9092.87: 9200.32},
                DBAPIError,
                "(conversion from dict to Decimal is not supported)"
            ],
            [{}, DBAPIError, "(conversion from dict to Decimal is not supported)"],
            [(1898.14, 1892.74), DBAPIError, "argument must be a sequence of length 3"],
            [(), DBAPIError, "(argument must be a sequence of length 3)"],
            [
                datetime.now(),
                DBAPIError,
                "(conversion from datetime.datetime to Decimal is not supported)"
            ]
        ]
        await self.create_item(valid_data, invalid_data, "sample_numeric", db_session)

    async def test_datetime_field_validation(self, db_session):
        valid_data = [
            datetime(2025, 6, 8, 18, 19, 37, 718543),
            datetime.now(),
            (datetime(2025, 6, 8, 18, 19, 37, 718543)),
            "2025-06-05",
            "2025-06-05 21:18:52",
            "2025-06-05 21:18:52.123456+0400",
            "2023-12-25 14:30:00.123456",
            "2023-12-25T14:30:00",
            "2023-12-25T14:30:00Z",
            "2023-12-25T14:30:00.123456",
            "2023-12-25T14:30:00.123456Z",
            "2023-12-25T14:30:00.123456+04:00",
            "2023-12-25T14:30:00+04:00",
        ]
        invalid_data = [
            [
                9915,
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'int')"
            ],
            [
                9679.36,
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'float')"
            ],
            ["test", ValueError, "Invalid datetime format: test"],
            [
                True,
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'bool')"
            ],
            [
                datetime(1, 1, 1, 1, 1, 1, 1),
                DBAPIError,
                "\\(\\[Errno 22\\] Invalid argument\\)"
            ],
            [
                [datetime(2025, 1, 4)],
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'list')"
            ],
            [
                [datetime(2024, 10, 9), datetime(2024, 11, 30)],
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'list')"
            ],
            [
                [],
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'list')"
            ],
            [
                {datetime(2024, 8, 21)},
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'set')"
            ],
            [
                {datetime(2023, 8, 20), datetime(2023, 7, 7)},
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'set')"
            ],
            [
                {datetime(2022, 7, 5): datetime(2022, 12, 21)},
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'dict')"
            ],
            [
                {},
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'dict')"
            ],
            [
                (datetime(2024, 3, 13), datetime(2028, 1, 4)),
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'tuple')"
            ],
            [
                (),
                DBAPIError,
                "(expected a datetime.date or datetime.datetime instance, got 'tuple')"
            ],
            ["05-06-2025", ValueError, "Invalid datetime format: 05-06-2025"],
            ["10:00:14", ValueError, "Invalid datetime format: 10:00:14"],
            [
                "2025-06-05 21:18:52.123456+04",
                ValueError,
                "Invalid datetime format: 2025-06-05 21:18:52\\.123456\\+04"
            ],
            [
                "2025-06-02 23:20:35+08",
                ValueError, "Invalid datetime format: 2025-06-02 23:20:35\\+08"
            ]
        ]

        await self.create_item(valid_data, invalid_data, "sample_datetime", db_session)

    async def test_jsonb_field_validation(self, db_session):
        valid_data = [
            "test", 9999, True, 9999.99, ["test"], ["test1", "test2"], [],
            {"key": "value"}, {}, {9999: 9999}, {41: "value"}, {False: True},
            {True: "value"}, {9999.99: 9999.99}, {65.12: "value"}, {"key": "value"},
            ("test"), ("test1", "test2"), ()
        ]
        invalid_data = [
            [
                datetime(2025, 6, 9, 21, 59, 23, 994308),
                StatementError,
                "Object of type datetime is not JSON serializable"
            ],
            [
                {"test5", "test6"},
                StatementError,
                "Object of type set is not JSON serializable"
            ],
            [
                {"test7"},
                StatementError,
                "Object of type set is not JSON serializable"
            ],
            [
                {
                    datetime(2025, 6, 9, 21, 59, 23, 994308):
                    datetime(2025, 6, 9, 21, 59, 23, 994308)
                },
                StatementError,
                "keys must be str, int, float, bool or None, not datetime.datetime"
            ],
            [
                {datetime(2025, 6, 9, 21, 59, 23, 994308): "value"},
                StatementError,
                "keys must be str, int, float, bool or None, not datetime.datetime"
            ]
        ]

        await self.create_item(valid_data, invalid_data, "sample_jsonb", db_session)

    async def test_enum_field_validation(self, db_session):
        valid_data = [
            SampleEnum.FIRST, "FIRST",
            SampleEnum.SECOND, "SECOND",
            SampleEnum.THIRD, "THIRD",
            "   THIRD   ",
            (SampleEnum.FIRST),
        ]
        invalid_data = [
            [
                "second", DBAPIError,
                "nilai masukan tidak valid untuk enum sampleenum : « second »"
            ],
            [
                "aaaaaaaaa", DBAPIError,
                "nilai masukan tidak valid untuk enum sampleenum : « aaaaaaaaa »"
            ],
            [
                "aaa", DBAPIError,
                "nilai masukan tidak valid untuk enum sampleenum : « aaa »"
            ],
            [
                123, StatementError,
                "'123' is not among the defined enum values. Enum name: "
                "sampleenum. Possible values: FIRST, SECOND, THIRD"
            ],
            [
                12.3, StatementError,
                "'12.3' is not among the defined enum values. Enum name: "
                "sampleenum. Possible values: FIRST, SECOND, THIRD"
            ],
            [
                True, StatementError,
                "'True' is not among the defined enum values. Enum name: "
                "sampleenum. Possible values: FIRST, SECOND, THIRD"
            ],
            [
                datetime(2025, 7, 5, 8, 24, 30, 157344), StatementError,
                "'2025-07-05 08:24:30.157344' is not among the defined enum "
                "values. Enum name: sampleenum. Possible values: FIRST, "
                "SECOND, THIRD"
            ],
            [[SampleEnum.FIRST], StatementError, "unhashable type: 'list'"],
            [[], StatementError, "unhashable type: 'list'"],
            [
                [SampleEnum.SECOND, SampleEnum.THIRD], StatementError,
                "unhashable type: 'list'"
            ],
            [{SampleEnum.FIRST}, StatementError, "unhashable type: 'set'"],
            [
                {SampleEnum.SECOND, SampleEnum.THIRD}, StatementError,
                "unhashable type: 'set'"
            ],
            [{}, StatementError, "unhashable type: 'dict'"],
            [
                {SampleEnum.FIRST: SampleEnum.SECOND}, StatementError,
                "unhashable type: 'dict'"
            ],
            [
                (SampleEnum.SECOND, SampleEnum.THIRD), StatementError,
                "is not among the defined enum values. Enum name: "
                "sampleenum. Possible values: FIRST, SECOND, THIRD"
            ],
            [
                (), StatementError,
                "is not among the defined enum values. Enum name: "
                "sampleenum. Possible values: FIRST, SECOND, THIRD"
            ],
        ]

        await self.create_item(valid_data, invalid_data, "sample_enum", db_session)
