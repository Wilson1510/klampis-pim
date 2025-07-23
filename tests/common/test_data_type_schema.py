import enum
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Union, Any

import pytest
from pydantic import (
    BaseModel, ValidationError, EmailStr, HttpUrl,
    StrictStr, StrictInt, StrictFloat, StrictBool
)
from app.schemas.base import StrictNonNegativeInt


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
    sample_str: str  # Done
    sample_int: int  # Done
    sample_float: float  # Done
    sample_bool: bool  # Done

    # Strict Types
    sample_strict_str: StrictStr  # Done
    sample_strict_int: StrictInt  # Done
    sample_strict_float: StrictFloat  # Done
    sample_strict_bool: StrictBool  # Done

    # Strict Non-Negative Types
    sample_strict_non_negative_int: StrictNonNegativeInt

    # Datetime types
    sample_datetime: datetime  # Done

    # Collection Types
    sample_list: List[Any]
    sample_dict: Dict[Any, Any]  # Done
    sample_set: Set[Any]
    sample_tuple: Tuple[Any, ...]

    # Optional & Union Types
    sample_optional: Optional[str] = None
    sample_union: Union[str, int]

    # String Specialized Types
    sample_email: EmailStr
    sample_url: HttpUrl

    # Numeric Specialized Types
    sample_decimal: Decimal

    # Enum Types
    sample_str_enum: SampleEnum  # Done
    sample_int_enum: SampleIntEnum  # Done

    # Complex/Nested Types
    sample_nested_model: NestedModel

    # File & Path Types
    sample_path: Path


class TestDataTypeSchema:

    def create_item(self, valid_data, invalid_data, target_field):
        """Helper method to test valid and invalid data for a specific field"""
        # Test valid data
        for data in valid_data:
            print(f"valid data: {data}")
            # try:
            # Create minimal schema with only the target field
            schema_data = self._get_minimal_valid_data()
            schema_data[target_field] = data
            schema = SampleSchemaDataType(**schema_data)
            assert getattr(schema, target_field) is not None
            # except Exception as e:
            #     pytest.fail(
            #         f"Valid data {data} failed for field {target_field}: {e}"
            #     )

        # Test invalid data
        for data, error_type, error_message in invalid_data:
            print(f"invalid data: {data}")
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
            "sample_strict_str": "test",
            "sample_strict_int": 42,
            "sample_strict_float": 3.14,
            "sample_strict_bool": True,
            "sample_strict_non_negative_int": 42,
            "sample_datetime": datetime(2025, 1, 1, 12, 0, 0),
            "sample_list": ["item1", "item2"],
            "sample_dict": {"key1": 1, "key2": 2},
            "sample_set": {"item1", "item2"},
            "sample_tuple": ("str", 42, True),
            "sample_union": "union_string",
            "sample_email": "test@example.com",
            "sample_url": "https://example.com",
            "sample_decimal": Decimal("123.45"),
            "sample_str_enum": SampleEnum.FIRST,
            "sample_int_enum": SampleIntEnum.ONE,
            "sample_nested_model": {"nested_field": "test", "nested_number": 42},
            "sample_path": Path("/tmp/test")
        }

    def test_str_field_validation(self):
        """Test string field validation"""
        valid_data = [
            "test", "test with spaces", "  test with whitespace   ", ("test"), "",
            "    ", "1test", "test*"
        ]
        invalid_data = [
            [123, ValidationError, "Input should be a valid string"],
            [12.3, ValidationError, "Input should be a valid string"],
            [True, ValidationError, "Input should be a valid string"],
            [['test'], ValidationError, "Input should be a valid string"],
            [['test1', 'test2'], ValidationError, "Input should be a valid string"],
            [[], ValidationError, "Input should be a valid string"],
            [{'test1', 'test2'}, ValidationError, "Input should be a valid string"],
            [{'test'}, ValidationError, "Input should be a valid string"],
            [
                {'test key': 'test value'},
                ValidationError,
                "Input should be a valid string"
            ],
            [{}, ValidationError, "Input should be a valid string"],
            [('test1', 'test2'), ValidationError, "Input should be a valid string"],
            [(), ValidationError, "Input should be a valid string"],
            [datetime.now(), ValidationError, "Input should be a valid string"]
        ]

        self.create_item(valid_data, invalid_data, "sample_str")

    def test_int_field_validation(self):
        """Test integer field validation"""
        valid_data = [
            -99999, 0, 00, 99999, 2147483647, -2147483648, True, 999.00, "999", (88)
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid integer"],
            [999.99, ValidationError, "Input should be a valid integer"],
            [[999], ValidationError, "Input should be a valid integer"],
            [[998, 999], ValidationError, "Input should be a valid integer"],
            [[], ValidationError, "Input should be a valid integer"],
            [{999}, ValidationError, "Input should be a valid integer"],
            [{998, 999}, ValidationError, "Input should be a valid integer"],
            [{998: 999}, ValidationError, "Input should be a valid integer"],
            [{}, ValidationError, "Input should be a valid integer"],
            [(998, 999), ValidationError, "Input should be a valid integer"],
            [(), ValidationError, "Input should be a valid integer"],
            [datetime.now(), ValidationError, "Input should be a valid integer"]
        ]

        self.create_item(valid_data, invalid_data, "sample_int")

    def test_bool_field_validation(self):
        """Test boolean field validation"""
        valid_data = [
            True, False, (True), "yes", "no", "true", "false", 1.0, 0.0, 1, 0
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid boolean"],
            [2, ValidationError, "Input should be a valid boolean"],
            [999, ValidationError, "Input should be a valid boolean"],
            [9.99, ValidationError, "Input should be a valid boolean"],
            [[False], ValidationError, "Input should be a valid boolean"],
            [[True, False], ValidationError, "Input should be a valid boolean"],
            [[], ValidationError, "Input should be a valid boolean"],
            [{True}, ValidationError, "Input should be a valid boolean"],
            [{False, True}, ValidationError, "Input should be a valid boolean"],
            [{True: True}, ValidationError, "Input should be a valid boolean"],
            [{}, ValidationError, "Input should be a valid boolean"],
            [
                datetime(2025, 6, 8, 18, 19, 37, 718543),
                ValidationError,
                "Input should be a valid boolean"
            ],
            [(True, False), ValidationError, "Input should be a valid boolean"],
            [(), ValidationError, "Input should be a valid boolean"]
        ]

        self.create_item(valid_data, invalid_data, "sample_bool")

    def test_float_field_validation(self):
        """Test float field validation"""
        valid_data = [
            -9999999999.99, 0.0, 88.14, 2025, 9999999999.99, False, "9999.99", (88.0),
            "9999"
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid number"],
            [[9999.99], ValidationError, "Input should be a valid number"],
            [[9999, 9999, 9999], ValidationError, "Input should be a valid number"],
            [[], ValidationError, "Input should be a valid number"],
            [{9999.99}, ValidationError, "Input should be a valid number"],
            [{9999.99, 9999.99}, ValidationError, "Input should be a valid number"],
            [{9999.99: 9999.99}, ValidationError, "Input should be a valid number"],
            [{}, ValidationError, "Input should be a valid number"],
            [(9999.99, 9999.99), ValidationError, "Input should be a valid number"],
            [(), ValidationError, "Input should be a valid number"],
            [datetime.now(), ValidationError, "Input should be a valid number"]
        ]

        self.create_item(valid_data, invalid_data, "sample_float")

    def test_datetime_field_validation(self):
        """Test datetime field validation"""
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
            9915,
            9679.36,
            datetime(1, 1, 1, 1, 1, 1, 1),
        ]
        invalid_data = [
            [
                "test",
                ValidationError,
                "Input should be a valid datetime or date, input is too short"
            ],
            [True, ValidationError, "Input should be a valid datetime"],
            [
                [datetime(2025, 1, 4)],
                ValidationError,
                "Input should be a valid datetime"
            ],
            [
                [datetime(2024, 10, 9), datetime(2024, 11, 30)],
                ValidationError,
                "Input should be a valid datetime"
            ],
            [
                [],
                ValidationError,
                "Input should be a valid datetime"
            ],
            [
                {datetime(2024, 8, 21)},
                ValidationError,
                "Input should be a valid datetime"
            ],
            [
                {datetime(2023, 8, 20), datetime(2023, 7, 7)},
                ValidationError,
                "Input should be a valid datetime"
            ],
            [
                {datetime(2022, 7, 5): datetime(2022, 12, 21)},
                ValidationError,
                "Input should be a valid datetime"
            ],
            [
                {},
                ValidationError,
                "Input should be a valid datetime"
            ],
            [
                (datetime(2024, 3, 13), datetime(2028, 1, 4)),
                ValidationError,
                "Input should be a valid datetime"
            ],
            [
                (),
                ValidationError,
                "Input should be a valid datetime"
            ],
            [
                "05-06-2025",
                ValidationError,
                "Input should be a valid datetime or date, invalid character in year"
            ],
            [
                "10:00:14",
                ValidationError,
                "Input should be a valid datetime or date, input is too short"
            ],
            [
                "2025-06-05 21:18:52.123456+04",
                ValidationError,
                "Input should be a valid datetime or date,"
                " unexpected extra characters at the end of the input"
            ],
            [
                "2025-06-02 23:20:35+08",
                ValidationError,
                "Input should be a valid datetime or date, "
                "unexpected extra characters at the end of the input"
            ]
        ]

        self.create_item(valid_data, invalid_data, "sample_datetime")

    def test_strict_str_field_validation(self):
        """Test strict string field validation"""
        valid_data = [
            "test", "test with spaces", "  test with whitespace   ", ("test"), "",
            "    ", "1test", "test*"
        ]
        invalid_data = [
            [123, ValidationError, "Input should be a valid string"],
            [12.3, ValidationError, "Input should be a valid string"],
            [True, ValidationError, "Input should be a valid string"],
            [['test'], ValidationError, "Input should be a valid string"],
            [['test1', 'test2'], ValidationError, "Input should be a valid string"],
            [[], ValidationError, "Input should be a valid string"],
            [{'test1', 'test2'}, ValidationError, "Input should be a valid string"],
            [{'test'}, ValidationError, "Input should be a valid string"],
            [
                {'test key': 'test value'},
                ValidationError,
                "Input should be a valid string"
            ],
            [{}, ValidationError, "Input should be a valid string"],
            [('test1', 'test2'), ValidationError, "Input should be a valid string"],
            [(), ValidationError, "Input should be a valid string"],
            [datetime.now(), ValidationError, "Input should be a valid string"]
        ]

        self.create_item(valid_data, invalid_data, "sample_strict_str")

    def test_strict_int_field_validation(self):
        """Test integer field validation"""
        valid_data = [
            -99999, 0, 00, 99999, 2147483647, -2147483648, (88)
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid integer"],
            ["999", ValidationError, "Input should be a valid integer"],
            [True, ValidationError, "Input should be a valid integer"],
            [999.00, ValidationError, "Input should be a valid integer"],
            [999.99, ValidationError, "Input should be a valid integer"],
            [[999], ValidationError, "Input should be a valid integer"],
            [[998, 999], ValidationError, "Input should be a valid integer"],
            [[], ValidationError, "Input should be a valid integer"],
            [{999}, ValidationError, "Input should be a valid integer"],
            [{998, 999}, ValidationError, "Input should be a valid integer"],
            [{998: 999}, ValidationError, "Input should be a valid integer"],
            [{}, ValidationError, "Input should be a valid integer"],
            [(998, 999), ValidationError, "Input should be a valid integer"],
            [(), ValidationError, "Input should be a valid integer"],
            [datetime.now(), ValidationError, "Input should be a valid integer"]
        ]

        self.create_item(valid_data, invalid_data, "sample_strict_int")

    def test_strict_bool_field_validation(self):
        """Test strict boolean field validation"""
        valid_data = [True, False, (True)]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid boolean"],
            ["yes", ValidationError, "Input should be a valid boolean"],
            ["no", ValidationError, "Input should be a valid boolean"],
            ["true", ValidationError, "Input should be a valid boolean"],
            ["false", ValidationError, "Input should be a valid boolean"],
            [1.0, ValidationError, "Input should be a valid boolean"],
            [0.0, ValidationError, "Input should be a valid boolean"],
            [1, ValidationError, "Input should be a valid boolean"],
            [0, ValidationError, "Input should be a valid boolean"],
            [2, ValidationError, "Input should be a valid boolean"],
            [999, ValidationError, "Input should be a valid boolean"],
            [9.99, ValidationError, "Input should be a valid boolean"],
            [[False], ValidationError, "Input should be a valid boolean"],
            [[True, False], ValidationError, "Input should be a valid boolean"],
            [[], ValidationError, "Input should be a valid boolean"],
            [{True}, ValidationError, "Input should be a valid boolean"],
            [{False, True}, ValidationError, "Input should be a valid boolean"],
            [{True: True}, ValidationError, "Input should be a valid boolean"],
            [{}, ValidationError, "Input should be a valid boolean"],
            [
                datetime(2025, 6, 8, 18, 19, 37, 718543),
                ValidationError,
                "Input should be a valid boolean"
            ],
            [(True, False), ValidationError, "Input should be a valid boolean"],
            [(), ValidationError, "Input should be a valid boolean"]
        ]

        self.create_item(valid_data, invalid_data, "sample_strict_bool")

    def test_strict_float_field_validation(self):
        """Test strict float field validation"""
        valid_data = [
            -9999999999.99, 0.0, 88.14, 9999999999.99, (88.0), 2025
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid number"],
            [False, ValidationError, "Input should be a valid number"],
            ["9999", ValidationError, "Input should be a valid number"],
            ["9999.99", ValidationError, "Input should be a valid number"],
            [[9999.99], ValidationError, "Input should be a valid number"],
            [[9999, 9999, 9999], ValidationError, "Input should be a valid number"],
            [[], ValidationError, "Input should be a valid number"],
            [{9999.99}, ValidationError, "Input should be a valid number"],
            [{9999.99, 9999.99}, ValidationError, "Input should be a valid number"],
            [{9999.99: 9999.99}, ValidationError, "Input should be a valid number"],
            [{}, ValidationError, "Input should be a valid number"],
            [(9999.99, 9999.99), ValidationError, "Input should be a valid number"],
            [(), ValidationError, "Input should be a valid number"],
            [datetime.now(), ValidationError, "Input should be a valid number"]
        ]

        self.create_item(valid_data, invalid_data, "sample_strict_float")

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
            {"key": "value"}, {}, {9999: 9999}, {41: "value"}, {False: True},
            {True: "value"}, {9999.99: 9999.99}, {65.12: "value"}, {"key": "value"},
            {
                    datetime(2025, 6, 8, 18, 19, 37, 718543):
                    datetime(2025, 6, 8, 18, 19, 37, 718543)
            },
            {datetime(2025, 6, 8, 18, 19, 37, 718543): "value"}
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid dictionary"],
            [123, ValidationError, "Input should be a valid dictionary"],
            [True, ValidationError, "Input should be a valid dictionary"],
            [9999.99, ValidationError, "Input should be a valid dictionary"],
            [
                ["test`"],
                ValidationError,
                "Input should be a valid dictionary"
            ],
            [
                ["test1", "test2"],
                ValidationError,
                "Input should be a valid dictionary"
            ],
            [
                [],
                ValidationError,
                "Input should be a valid dictionary"
            ],
            [("test"), ValidationError, "Input should be a valid dictionary"],
            [("test1", "test2"), ValidationError, "Input should be a valid dictionary"],
            [(), ValidationError, "Input should be a valid dictionary"],
            [
                datetime(2025, 6, 8, 18, 19, 37, 718543),
                ValidationError,
                "Input should be a valid dictionary"
            ],
            [{"test5", "test6"}, ValidationError, "Input should be a valid dictionary"],
            [{"test7"}, ValidationError, "Input should be a valid dictionary"]
        ]

        self.create_item(valid_data, invalid_data, "sample_dict")

    def test_set_field_validation(self):
        """Test set field validation"""
        valid_data = [
            {"key": "value"}, {}, {9999: 9999}, {41: "value"}, {False: True},
            {True: "value"}, {9999.99: 9999.99}, {65.12: "value"}, {"key": "value"}
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid dictionary"],
            [123, ValidationError, "Input should be a valid dictionary"],
            [True, ValidationError, "Input should be a valid dictionary"],
            [9999.99, ValidationError, "Input should be a valid dictionary"],
            [
                ["test`"],
                ValidationError,
                "Input should be a valid dictionary"
            ],
            [
                ["test1", "test2"],
                ValidationError,
                "Input should be a valid dictionary"
            ],
            [
                [],
                ValidationError,
                "Input should be a valid dictionary"
            ],
            [("test"), ValidationError, "Input should be a valid dictionary"],
            [("test1", "test2"), ValidationError, "Input should be a valid dictionary"],
            [(), ValidationError, "Input should be a valid dictionary"],
            [
                datetime(2025, 6, 8, 18, 19, 37, 718543),
                ValidationError,
                "Input should be a valid dictionary"
            ],
            [{"test5", "test6"}, ValidationError, "Input should be a valid dictionary"],
            [{"test7"}, ValidationError, "Input should be a valid dictionary"],
            [
                {
                    datetime(2025, 6, 8, 18, 19, 37, 718543):
                    datetime(2025, 6, 8, 18, 19, 37, 718543)
                },
                ValidationError,
                "keys must be str, int, float, bool or None, not datetime.datetime"
            ],
            [
                {datetime(2025, 6, 8, 18, 19, 37, 718543): "value"},
                ValidationError,
                "keys must be str, int, float, bool or None, not datetime.datetime"
            ]
        ]

        self.create_item(valid_data, invalid_data, "sample_set")

    # def test_tuple_field_validation(self):
    #     """Test tuple field validation"""
    #     valid_data = [
    #         ("str", 42, True),
    #         ["str", 42, True],  # List can be converted to tuple
    #     ]
    #     invalid_data = [
    #         ["not_tuple", ValidationError, "Input should be a valid tuple"],
    #         [123, ValidationError, "Input should be a valid tuple"],
    #         [True, ValidationError, "Input should be a valid tuple"],
    #         [
    #             ("str", "not_int", True),
    #             ValidationError,
    #             "Input should be a valid integer",
    #         ],
    #         [("str", 42), ValidationError, "Tuple should have 3 items"],
    #         [
    #             ("str", 42, True, "extra"),
    #             ValidationError,
    #             "Tuple should have 3 items",
    #         ],
    #     ]

    #     self.create_item(valid_data, invalid_data, "sample_tuple")

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
            (SampleEnum.FIRST)
        ]
        invalid_data = [
            [
                "   THIRD   ",
                ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                "second", ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                "aaaaaaaaa", ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                "aaa", ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                123, ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                12.3, ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                True, ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                datetime(2025, 7, 5, 8, 24, 30, 157344), ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                [SampleEnum.FIRST],
                ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                [],
                ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                [SampleEnum.SECOND, SampleEnum.THIRD], ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                {SampleEnum.FIRST},
                ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                {SampleEnum.SECOND, SampleEnum.THIRD}, ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [{}, ValidationError, "Input should be 'FIRST', 'SECOND' or 'THIRD'"],
            [
                {SampleEnum.FIRST: SampleEnum.SECOND}, ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                (SampleEnum.SECOND, SampleEnum.THIRD), ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
            [
                (), ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ],
        ]

        self.create_item(valid_data, invalid_data, "sample_str_enum")

    def test_int_enum_field_validation(self):
        """Test integer enum field validation"""
        valid_data = [
            SampleIntEnum.ONE, SampleIntEnum.TWO, SampleIntEnum.THREE,
            1, 2, 3, (SampleIntEnum.ONE), "1", True
        ]
        invalid_data = [
            [4, ValidationError, "Input should be 1, 2 or 3"],
            [0, ValidationError, "Input should be 1, 2 or 3"],
            [[], ValidationError, "Input should be 1, 2 or 3"],
            [12.3, ValidationError, "Input should be 1, 2 or 3"],
            [
                datetime(2025, 7, 5, 8, 24, 30, 157344), ValidationError,
                "Input should be 1, 2 or 3"
            ],
            [[SampleIntEnum.ONE], ValidationError, "Input should be 1, 2 or 3"],
            [[], ValidationError, "Input should be 1, 2 or 3"],
            [
                [SampleIntEnum.TWO, SampleIntEnum.THREE], ValidationError,
                "Input should be 1, 2 or 3"
            ],
            [{SampleIntEnum.ONE}, ValidationError, "Input should be 1, 2 or 3"],
            [
                {SampleIntEnum.TWO, SampleIntEnum.THREE}, ValidationError,
                "Input should be 1, 2 or 3"
            ],
            [{}, ValidationError, "Input should be 1, 2 or 3"],
            [
                {SampleIntEnum.ONE: SampleIntEnum.TWO}, ValidationError,
                "Input should be 1, 2 or 3"
            ],
            [
                (SampleIntEnum.TWO, SampleIntEnum.THREE), ValidationError,
                "Input should be 1, 2 or 3"
            ],
            [(), ValidationError, "Input should be 1, 2 or 3"]
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
