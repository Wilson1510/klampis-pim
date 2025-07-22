import enum
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Union, FrozenSet
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel, ValidationError, EmailStr, HttpUrl
from pydantic.types import (
    PositiveInt, NegativeInt, PositiveFloat, NegativeFloat
)


class SampleEnum(str, enum.Enum):
    FIRST = "FIRST"
    SECOND = "SECOND"
    THIRD = "THIRD"


class SampleIntEnum(int, enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3


class NestedModel(BaseModel):
    nested_field: str
    nested_number: int


class SampleSchemaDataType(BaseModel):
    """Sample schema for testing various Pydantic data types."""

    # Basic/Primitive Types
    sample_str: str
    sample_int: int
    sample_float: float
    sample_bool: bool
    sample_bytes: bytes

    # Date & Time Types
    sample_datetime: datetime
    sample_date: date
    sample_time: time
    sample_timedelta: timedelta

    # Collection Types
    sample_list: List[str]
    sample_dict: Dict[str, int]
    sample_set: Set[str]
    sample_tuple: Tuple[str, int, bool]
    sample_frozenset: FrozenSet[str]

    # Optional & Union Types
    sample_optional: Optional[str] = None
    sample_union: Union[str, int]

    # String Specialized Types
    sample_email: EmailStr
    sample_url: HttpUrl
    sample_uuid: UUID

    # Numeric Specialized Types
    sample_positive_int: PositiveInt
    sample_negative_int: NegativeInt
    sample_positive_float: PositiveFloat
    sample_negative_float: NegativeFloat
    sample_decimal: Decimal

    # Enum Types
    sample_str_enum: SampleEnum
    sample_int_enum: SampleIntEnum

    # Complex/Nested Types
    sample_nested_model: NestedModel

    # File & Path Types
    sample_path: Path


class TestDataTypeSchema:

    def create_item(self, valid_data, invalid_data, target_field):
        """Helper method to test valid and invalid data for a specific field"""
        # Test valid data
        for data in valid_data:
            try:
                # Create minimal schema with only the target field
                schema_data = self._get_minimal_valid_data()
                schema_data[target_field] = data
                schema = SampleSchemaDataType(**schema_data)
                assert getattr(schema, target_field) is not None
            except Exception as e:
                pytest.fail(
                    f"Valid data {data} failed for field {target_field}: {e}"
                )

        # Test invalid data
        for data, error_type, error_message in invalid_data:
            schema_data = self._get_minimal_valid_data()
            schema_data[target_field] = data

            with pytest.raises(error_type, match=error_message):
                SampleSchemaDataType(**schema_data)

    def _get_minimal_valid_data(self):
        """Returns minimal valid data for creating schema instances"""
        return {
            "sample_str": "test",
            "sample_int": 42,
            "sample_float": 3.14,
            "sample_bool": True,
            "sample_bytes": b"test",
            "sample_datetime": datetime(2025, 1, 1, 12, 0, 0),
            "sample_date": date(2025, 1, 1),
            "sample_time": time(12, 0, 0),
            "sample_timedelta": timedelta(days=1),
            "sample_list": ["item1", "item2"],
            "sample_dict": {"key1": 1, "key2": 2},
            "sample_set": {"item1", "item2"},
            "sample_tuple": ("str", 42, True),
            "sample_frozenset": frozenset(["item1", "item2"]),
            "sample_union": "union_string",
            "sample_email": "test@example.com",
            "sample_url": "https://example.com",
            "sample_uuid": uuid4(),
            "sample_positive_int": 10,
            "sample_negative_int": -10,
            "sample_positive_float": 3.14,
            "sample_negative_float": -3.14,
            "sample_decimal": Decimal("123.45"),
            "sample_str_enum": SampleEnum.FIRST,
            "sample_int_enum": SampleIntEnum.ONE,
            "sample_nested_model": {"nested_field": "test", "nested_number": 42},
            "sample_path": Path("/tmp/test")
        }

    def test_str_field_validation(self):
        """Test string field validation"""
        valid_data = [
            "test", "test with spaces", "  test with whitespace   ",
            "", "    ", "123", "test123", "Test_With_Underscores",
            "test-with-dashes", "test.with.dots", "test/with/slashes"
        ]
        invalid_data = [
            [123, ValidationError, "Input should be a valid string"],
            [12.3, ValidationError, "Input should be a valid string"],
            [True, ValidationError, "Input should be a valid string"],
            [['test'], ValidationError, "Input should be a valid string"],
            [{'test': 'value'}, ValidationError, "Input should be a valid string"],
            [datetime.now(), ValidationError, "Input should be a valid string"],
        ]

        self.create_item(valid_data, invalid_data, "sample_str")

    def test_int_field_validation(self):
        """Test integer field validation"""
        valid_data = [-99999, 0, 99999, 2147483647, -2147483648]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid integer"],
            [999.99, ValidationError, "Input should be a valid integer"],
            [True, ValidationError, "Input should be a valid integer"],
            [[999], ValidationError, "Input should be a valid integer"],
            [{'key': 999}, ValidationError, "Input should be a valid integer"],
            [datetime.now(), ValidationError, "Input should be a valid integer"],
        ]

        self.create_item(valid_data, invalid_data, "sample_int")

    def test_float_field_validation(self):
        """Test float field validation"""
        valid_data = [-99999.99, 0.0, 88.14, 2025, 99999.99, 3.14159]
        invalid_data = [
            ["9999.99", ValidationError, "Input should be a valid number"],
            [True, ValidationError, "Input should be a valid number"],
            [[9999.99], ValidationError, "Input should be a valid number"],
            [{'key': 9999.99}, ValidationError, "Input should be a valid number"],
            [datetime.now(), ValidationError, "Input should be a valid number"],
        ]

        self.create_item(valid_data, invalid_data, "sample_float")

    def test_bool_field_validation(self):
        """Test boolean field validation"""
        valid_data = [True, False]
        invalid_data = [
            ["true", ValidationError, "Input should be a valid boolean"],
            ["false", ValidationError, "Input should be a valid boolean"],
            [1, ValidationError, "Input should be a valid boolean"],
            [0, ValidationError, "Input should be a valid boolean"],
            [1.0, ValidationError, "Input should be a valid boolean"],
            [[], ValidationError, "Input should be a valid boolean"],
            [datetime.now(), ValidationError, "Input should be a valid boolean"],
        ]

        self.create_item(valid_data, invalid_data, "sample_bool")

    def test_bytes_field_validation(self):
        """Test bytes field validation"""
        valid_data = [b"test", b"", b"test with spaces", bytes("test", "utf-8")]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid bytes"],
            [123, ValidationError, "Input should be a valid bytes"],
            [True, ValidationError, "Input should be a valid bytes"],
            [['test'], ValidationError, "Input should be a valid bytes"],
            [datetime.now(), ValidationError, "Input should be a valid bytes"],
        ]

        self.create_item(valid_data, invalid_data, "sample_bytes")

    def test_datetime_field_validation(self):
        """Test datetime field validation"""
        valid_data = [
            datetime(2025, 6, 8, 18, 19, 37, 718543),
            datetime.now(),
            "2025-06-05T21:18:52",
            "2025-06-05 21:18:52",
            "2025-06-05T21:18:52.123456",
            "2025-06-05T21:18:52Z",
            "2025-06-05T21:18:52+04:00",
        ]
        invalid_data = [
            [9915, ValidationError, "Input should be a valid datetime"],
            [9679.36, ValidationError, "Input should be a valid datetime"],
            ["test", ValidationError, "Input should be a valid datetime"],
            [True, ValidationError, "Input should be a valid datetime"],
            ["05-06-2025", ValidationError, "Input should be a valid datetime"],
            ["10:00:14", ValidationError, "Input should be a valid datetime"],
            [[], ValidationError, "Input should be a valid datetime"],
        ]

        self.create_item(valid_data, invalid_data, "sample_datetime")

    def test_date_field_validation(self):
        """Test date field validation"""
        valid_data = [
            date(2025, 6, 8),
            date.today(),
            "2025-06-05",
            datetime(2025, 6, 8, 18, 19, 37),  # datetime can be converted to date
        ]
        invalid_data = [
            [9915, ValidationError, "Input should be a valid date"],
            ["test", ValidationError, "Input should be a valid date"],
            [True, ValidationError, "Input should be a valid date"],
            ["05-06-2025", ValidationError, "Input should be a valid date"],
            [[], ValidationError, "Input should be a valid date"],
        ]

        self.create_item(valid_data, invalid_data, "sample_date")

    def test_time_field_validation(self):
        """Test time field validation"""
        valid_data = [
            time(12, 30, 45),
            time(0, 0, 0),
            time(23, 59, 59),
            "12:30:45",
            "12:30",
            "12:30:45.123456",
        ]
        invalid_data = [
            [9915, ValidationError, "Input should be a valid time"],
            ["test", ValidationError, "Input should be a valid time"],
            [True, ValidationError, "Input should be a valid time"],
            ["25:30:45", ValidationError, "Input should be a valid time"],
            [[], ValidationError, "Input should be a valid time"],
        ]

        self.create_item(valid_data, invalid_data, "sample_time")

    def test_timedelta_field_validation(self):
        """Test timedelta field validation"""
        valid_data = [
            timedelta(days=1),
            timedelta(hours=2),
            timedelta(minutes=30),
            timedelta(seconds=45),
            timedelta(days=1, hours=2, minutes=30),
            "P1D",  # ISO 8601 duration
            "PT2H30M",  # ISO 8601 duration
        ]
        invalid_data = [
            [9915, ValidationError, "Input should be a valid timedelta"],
            ["test", ValidationError, "Input should be a valid timedelta"],
            [True, ValidationError, "Input should be a valid timedelta"],
            [[], ValidationError, "Input should be a valid timedelta"],
        ]

        self.create_item(valid_data, invalid_data, "sample_timedelta")

    def test_list_field_validation(self):
        """Test list field validation"""
        valid_data = [
            ["item1", "item2"],
            [],
            ["single_item"],
            ["item1", "item2", "item3", "item4"],
        ]
        invalid_data = [
            ["not_a_list", ValidationError, "Input should be a valid list"],
            [123, ValidationError, "Input should be a valid list"],
            [True, ValidationError, "Input should be a valid list"],
            [{"key": "value"}, ValidationError, "Input should be a valid list"],
            [["item1", 123], ValidationError, "Input should be a valid string"],
        ]

        self.create_item(valid_data, invalid_data, "sample_list")

    def test_dict_field_validation(self):
        """Test dict field validation"""
        valid_data = [
            {"key1": 1, "key2": 2},
            {},
            {"single_key": 42},
        ]
        invalid_data = [
            ["not_a_dict", ValidationError, "Input should be a valid dictionary"],
            [123, ValidationError, "Input should be a valid dictionary"],
            [True, ValidationError, "Input should be a valid dictionary"],
            [[], ValidationError, "Input should be a valid dictionary"],
            [
                {"key1": "not_int"},
                ValidationError,
                "Input should be a valid integer",
            ],
        ]

        self.create_item(valid_data, invalid_data, "sample_dict")

    def test_set_field_validation(self):
        """Test set field validation"""
        valid_data = [
            {"item1", "item2"},
            set(),
            {"single_item"},
            ["item1", "item2"],  # List can be converted to set
        ]
        invalid_data = [
            ["not_a_set", ValidationError, "Input should be a valid set"],
            [123, ValidationError, "Input should be a valid set"],
            [True, ValidationError, "Input should be a valid set"],
            [{"key": "value"}, ValidationError, "Input should be a valid set"],
        ]

        self.create_item(valid_data, invalid_data, "sample_set")

    def test_tuple_field_validation(self):
        """Test tuple field validation"""
        valid_data = [
            ("str", 42, True),
            ["str", 42, True],  # List can be converted to tuple
        ]
        invalid_data = [
            ["not_tuple", ValidationError, "Input should be a valid tuple"],
            [123, ValidationError, "Input should be a valid tuple"],
            [True, ValidationError, "Input should be a valid tuple"],
            [
                ("str", "not_int", True),
                ValidationError,
                "Input should be a valid integer",
            ],
            [("str", 42), ValidationError, "Tuple should have 3 items"],
            [
                ("str", 42, True, "extra"),
                ValidationError,
                "Tuple should have 3 items",
            ],
        ]

        self.create_item(valid_data, invalid_data, "sample_tuple")

    def test_frozenset_field_validation(self):
        """Test frozenset field validation"""
        valid_data = [
            frozenset(["item1", "item2"]),
            frozenset(),
            {"item1", "item2"},  # Set can be converted to frozenset
            ["item1", "item2"],  # List can be converted to frozenset
        ]
        invalid_data = [
            ["not_frozenset", ValidationError, "Input should be a valid frozenset"],
            [123, ValidationError, "Input should be a valid frozenset"],
            [True, ValidationError, "Input should be a valid frozenset"],
            [{"key": "value"}, ValidationError, "Input should be a valid frozenset"],
        ]

        self.create_item(valid_data, invalid_data, "sample_frozenset")

    def test_optional_field_validation(self):
        """Test optional field validation"""
        valid_data = [
            "test_string",
            None,
        ]
        invalid_data = [
            [123, ValidationError, "Input should be a valid string"],
            [True, ValidationError, "Input should be a valid string"],
            [[], ValidationError, "Input should be a valid string"],
        ]

        self.create_item(valid_data, invalid_data, "sample_optional")

    def test_union_field_validation(self):
        """Test union field validation"""
        valid_data = [
            "test_string",
            123,
            "456",  # String that looks like number
        ]
        invalid_data = [
            [True, ValidationError, "Input should be a valid string or integer"],
            [[], ValidationError, "Input should be a valid string or integer"],
            [
                {"key": "value"},
                ValidationError,
                "Input should be a valid string or integer",
            ],
            [3.14, ValidationError, "Input should be a valid string or integer"],
        ]

        self.create_item(valid_data, invalid_data, "sample_union")

    def test_email_field_validation(self):
        """Test email field validation"""
        valid_data = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org",
            "123@example.com",
        ]
        invalid_data = [
            ["not_an_email", ValidationError, "Input should be a valid email address"],
            ["@example.com", ValidationError, "Input should be a valid email address"],
            ["test@", ValidationError, "Input should be a valid email address"],
            [
                "test.example.com",
                ValidationError,
                "Input should be a valid email address",
            ],
            [123, ValidationError, "Input should be a valid string"],
            [[], ValidationError, "Input should be a valid string"],
        ]

        self.create_item(valid_data, invalid_data, "sample_email")

    def test_url_field_validation(self):
        """Test URL field validation"""
        valid_data = [
            "https://example.com",
            "http://example.com",
            "https://example.com/path",
            "https://example.com:8080",
            "ftp://example.com",
        ]
        invalid_data = [
            ["not_a_url", ValidationError, "Input should be a valid URL"],
            ["example.com", ValidationError, "Input should be a valid URL"],
            ["//example.com", ValidationError, "Input should be a valid URL"],
            [123, ValidationError, "Input should be a valid string"],
            [[], ValidationError, "Input should be a valid string"],
        ]

        self.create_item(valid_data, invalid_data, "sample_url")

    def test_uuid_field_validation(self):
        """Test UUID field validation"""
        valid_data = [
            uuid4(),
            "550e8400-e29b-41d4-a716-446655440000",
            "550e8400e29b41d4a716446655440000",  # Without hyphens
        ]
        invalid_data = [
            ["not_a_uuid", ValidationError, "Input should be a valid UUID"],
            [
                "550e8400-e29b-41d4-a716",
                ValidationError,
                "Input should be a valid UUID",
            ],
            [123, ValidationError, "Input should be a valid UUID"],
            [[], ValidationError, "Input should be a valid UUID"],
        ]

        self.create_item(valid_data, invalid_data, "sample_uuid")

    def test_positive_int_field_validation(self):
        """Test positive integer field validation"""
        valid_data = [1, 10, 999999, 2147483647]
        invalid_data = [
            [0, ValidationError, "Input should be greater than 0"],
            [-1, ValidationError, "Input should be greater than 0"],
            [-999, ValidationError, "Input should be greater than 0"],
            ["10", ValidationError, "Input should be a valid integer"],
            [10.5, ValidationError, "Input should be a valid integer"],
            [[], ValidationError, "Input should be a valid integer"],
        ]

        self.create_item(valid_data, invalid_data, "sample_positive_int")

    def test_negative_int_field_validation(self):
        """Test negative integer field validation"""
        valid_data = [-1, -10, -999999, -2147483648]
        invalid_data = [
            [0, ValidationError, "Input should be less than 0"],
            [1, ValidationError, "Input should be less than 0"],
            [999, ValidationError, "Input should be less than 0"],
            ["-10", ValidationError, "Input should be a valid integer"],
            [-10.5, ValidationError, "Input should be a valid integer"],
            [[], ValidationError, "Input should be a valid integer"],
        ]

        self.create_item(valid_data, invalid_data, "sample_negative_int")

    def test_positive_float_field_validation(self):
        """Test positive float field validation"""
        valid_data = [0.1, 1.0, 10.5, 999999.99]
        invalid_data = [
            [0.0, ValidationError, "Input should be greater than 0"],
            [-0.1, ValidationError, "Input should be greater than 0"],
            [-999.99, ValidationError, "Input should be greater than 0"],
            ["10.5", ValidationError, "Input should be a valid number"],
            [[], ValidationError, "Input should be a valid number"],
        ]

        self.create_item(valid_data, invalid_data, "sample_positive_float")

    def test_negative_float_field_validation(self):
        """Test negative float field validation"""
        valid_data = [-0.1, -1.0, -10.5, -999999.99]
        invalid_data = [
            [0.0, ValidationError, "Input should be less than 0"],
            [0.1, ValidationError, "Input should be less than 0"],
            [999.99, ValidationError, "Input should be less than 0"],
            ["-10.5", ValidationError, "Input should be a valid number"],
            [[], ValidationError, "Input should be a valid number"],
        ]

        self.create_item(valid_data, invalid_data, "sample_negative_float")

    def test_decimal_field_validation(self):
        """Test decimal field validation"""
        valid_data = [
            Decimal("123.45"),
            Decimal("0"),
            Decimal("-999.99"),
            "123.45",  # String can be converted to Decimal
            123.45,    # Float can be converted to Decimal
            123,       # Int can be converted to Decimal
        ]
        invalid_data = [
            ["not_a_number", ValidationError, "Input should be a valid decimal"],
            [True, ValidationError, "Input should be a valid decimal"],
            [[], ValidationError, "Input should be a valid decimal"],
            [{"key": "value"}, ValidationError, "Input should be a valid decimal"],
        ]

        self.create_item(valid_data, invalid_data, "sample_decimal")

    def test_str_enum_field_validation(self):
        """Test string enum field validation"""
        valid_data = [
            SampleEnum.FIRST,
            SampleEnum.SECOND,
            SampleEnum.THIRD,
            "FIRST",   # String can be converted to enum
            "SECOND",
            "THIRD",
        ]
        invalid_data = [
            ["FOURTH", ValidationError, "Input should be 'FIRST', 'SECOND' or 'THIRD'"],
            ["first", ValidationError, "Input should be 'FIRST', 'SECOND' or 'THIRD'"],
            [123, ValidationError, "Input should be 'FIRST', 'SECOND' or 'THIRD'"],
            [True, ValidationError, "Input should be 'FIRST', 'SECOND' or 'THIRD'"],
            [[], ValidationError, "Input should be 'FIRST', 'SECOND' or 'THIRD'"],
        ]

        self.create_item(valid_data, invalid_data, "sample_str_enum")

    def test_int_enum_field_validation(self):
        """Test integer enum field validation"""
        valid_data = [
            SampleIntEnum.ONE,
            SampleIntEnum.TWO,
            SampleIntEnum.THREE,
            1,   # Int can be converted to enum
            2,
            3,
        ]
        invalid_data = [
            [4, ValidationError, "Input should be 1, 2 or 3"],
            [0, ValidationError, "Input should be 1, 2 or 3"],
            ["1", ValidationError, "Input should be 1, 2 or 3"],
            [True, ValidationError, "Input should be 1, 2 or 3"],
            [[], ValidationError, "Input should be 1, 2 or 3"],
        ]

        self.create_item(valid_data, invalid_data, "sample_int_enum")

    def test_nested_model_field_validation(self):
        """Test nested model field validation"""
        valid_data = [
            NestedModel(nested_field="test", nested_number=42),
            {"nested_field": "test", "nested_number": 42},  # Dict can be converted
        ]
        invalid_data = [
            [{"nested_field": "test"}, ValidationError, "Field required"],
            [{"nested_number": 42}, ValidationError, "Field required"],
            [
                {"nested_field": 123, "nested_number": 42},
                ValidationError,
                "Input should be a valid string",
            ],
            [
                {"nested_field": "test", "nested_number": "not_int"},
                ValidationError,
                "Input should be a valid integer",
            ],
            [
                "not_a_model",
                ValidationError,
                "Input should be a valid dictionary or object",
            ],
            [123, ValidationError, "Input should be a valid dictionary or object"],
            [[], ValidationError, "Input should be a valid dictionary or object"],
        ]

        self.create_item(valid_data, invalid_data, "sample_nested_model")

    def test_path_field_validation(self):
        """Test path field validation"""
        valid_data = [
            Path("/tmp/test"),
            Path("relative/path"),
            "/tmp/test",        # String can be converted to Path
            "relative/path",
            ".",
            "..",
        ]
        invalid_data = [
            [123, ValidationError, "Input should be a valid path"],
            [True, ValidationError, "Input should be a valid path"],
            [[], ValidationError, "Input should be a valid path"],
            [{"key": "value"}, ValidationError, "Input should be a valid path"],
        ]

        self.create_item(valid_data, invalid_data, "sample_path")
