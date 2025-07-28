import enum
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Union, Any, Literal

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
    sample_strict_non_negative_int: StrictNonNegativeInt  # Done

    # Datetime types
    sample_datetime: datetime  # Done

    # Collection Types
    sample_list: List[Any]  # Done
    sample_dict: Dict[Any, Any]  # Done
    sample_set: Set[Any]  # Done
    sample_tuple: Tuple[Any, ...]  # Done

    # Optional & Union Types
    sample_optional: Optional[StrictStr] = None  # Done
    sample_union: Union[str, int]  # Done
    sample_literal: Literal["test", 25, False]  # Done

    # String Specialized Types
    sample_email: EmailStr  # Done
    sample_url: HttpUrl  # Done

    # Numeric Specialized Types
    sample_decimal: Decimal  # Done

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
            if target_field == "sample_optional" and data is None:
                assert schema.sample_optional is None
            else:
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
            "sample_literal": "test",
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
            [('test',), ValidationError, "Input should be a valid string"],
            [('test1', 'test2'), ValidationError, "Input should be a valid string"],
            [(), ValidationError, "Input should be a valid string"],
            [datetime.now(), ValidationError, "Input should be a valid string"],
            [None, ValidationError, "Input should be a valid string"]
        ]

        self.create_item(valid_data, invalid_data, "sample_str")

    def test_int_field_validation(self):
        """Test integer field validation"""
        valid_data = [
            -99999, 0, 00, 99999, 2147483647, -2147483648, True, 999.00, "999", (88)
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid integer"],
            [
                999.99,
                ValidationError,
                "Input should be a valid integer, got a number with a fractional part"
            ],
            [[999], ValidationError, "Input should be a valid integer"],
            [[998, 999], ValidationError, "Input should be a valid integer"],
            [[], ValidationError, "Input should be a valid integer"],
            [{999}, ValidationError, "Input should be a valid integer"],
            [{998, 999}, ValidationError, "Input should be a valid integer"],
            [{998: 999}, ValidationError, "Input should be a valid integer"],
            [{}, ValidationError, "Input should be a valid integer"],
            [(998, 999), ValidationError, "Input should be a valid integer"],
            [(998,), ValidationError, "Input should be a valid integer"],
            [(), ValidationError, "Input should be a valid integer"],
            [datetime.now(), ValidationError, "Input should be a valid integer"],
            [None, ValidationError, "Input should be a valid integer"]
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
            [(True,), ValidationError, "Input should be a valid boolean"],
            [(), ValidationError, "Input should be a valid boolean"],
            [None, ValidationError, "Input should be a valid boolean"]
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
            [(9999.99,), ValidationError, "Input should be a valid number"],
            [(), ValidationError, "Input should be a valid number"],
            [datetime.now(), ValidationError, "Input should be a valid number"],
            [None, ValidationError, "Input should be a valid number"]
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
                (datetime(2024, 3, 13),),
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
            ],
            [None, ValidationError, "Input should be a valid datetime"]
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
            [('test1',), ValidationError, "Input should be a valid string"],
            [(), ValidationError, "Input should be a valid string"],
            [datetime.now(), ValidationError, "Input should be a valid string"],
            [None, ValidationError, "Input should be a valid string"]
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
            [(998,), ValidationError, "Input should be a valid integer"],
            [(), ValidationError, "Input should be a valid integer"],
            [datetime.now(), ValidationError, "Input should be a valid integer"],
            [None, ValidationError, "Input should be a valid integer"]
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
            [(True,), ValidationError, "Input should be a valid boolean"],
            [(), ValidationError, "Input should be a valid boolean"],
            [None, ValidationError, "Input should be a valid boolean"]
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
            [(9999.99,), ValidationError, "Input should be a valid number"],
            [(), ValidationError, "Input should be a valid number"],
            [datetime.now(), ValidationError, "Input should be a valid number"],
            [None, ValidationError, "Input should be a valid number"]
        ]

        self.create_item(valid_data, invalid_data, "sample_strict_float")

    def test_strict_non_negative_int_field_validation(self):
        """Test strict non-negative integer field validation"""
        valid_data = [
            0, 00, 99999, 2147483647, (88)
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid integer"],
            ["999", ValidationError, "Input should be a valid integer"],
            [-99999, ValidationError, "Input should be greater than or equal to 0"],
            [
                -2147483648,
                ValidationError,
                "Input should be greater than or equal to 0"
            ],
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
            [(998,), ValidationError, "Input should be a valid integer"],
            [(), ValidationError, "Input should be a valid integer"],
            [datetime.now(), ValidationError, "Input should be a valid integer"],
            [None, ValidationError, "Input should be a valid integer"]
        ]

        self.create_item(valid_data, invalid_data, "sample_strict_non_negative_int")

    def test_list_field_validation(self):
        """Test list field validation"""
        valid_data = [
            ["item1", "item2"], [], ["single_item"], {'test'}, {'test1', 'test2'},
            ('test1', 'test2'), ()
        ]
        invalid_data = [
            ["not_a_list", ValidationError, "Input should be a valid list"],
            [123, ValidationError, "Input should be a valid list"],
            [12.3, ValidationError, "Input should be a valid list"],
            [True, ValidationError, "Input should be a valid list"],
            [{"key": "value"}, ValidationError, "Input should be a valid list"],
            [{}, ValidationError, "Input should be a valid list"],
            [('test'), ValidationError, "Input should be a valid list"],
            [datetime.now(), ValidationError, "Input should be a valid list"],
            [None, ValidationError, "Input should be a valid list"]
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
            [("test1",), ValidationError, "Input should be a valid dictionary"],
            [("test1", "test2"), ValidationError, "Input should be a valid dictionary"],
            [(), ValidationError, "Input should be a valid dictionary"],
            [
                datetime(2025, 6, 8, 18, 19, 37, 718543),
                ValidationError,
                "Input should be a valid dictionary"
            ],
            [{"test5", "test6"}, ValidationError, "Input should be a valid dictionary"],
            [{"test7"}, ValidationError, "Input should be a valid dictionary"],
            [None, ValidationError, "Input should be a valid dictionary"]
        ]

        self.create_item(valid_data, invalid_data, "sample_dict")

    def test_set_field_validation(self):
        """Test set field validation"""
        valid_data = [
            {"test"}, {"test", 1}, {True, 123.12, datetime.now()}, ['test'],
            ['test1', 'test2'], [], (), ("test1", "test2"), ("test1",)
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid set"],
            [123, ValidationError, "Input should be a valid set"],
            [True, ValidationError, "Input should be a valid set"],
            [9999.99, ValidationError, "Input should be a valid set"],
            [{"key": "value"}, ValidationError, "Input should be a valid set"],
            [{}, ValidationError, "Input should be a valid set"],
            [("test"), ValidationError, "Input should be a valid set"],
            [datetime.now(), ValidationError, "Input should be a valid set"],
            [None, ValidationError, "Input should be a valid set"]
        ]

        self.create_item(valid_data, invalid_data, "sample_set")

    def test_tuple_field_validation(self):
        """Test tuple field validation"""
        valid_data = [
            (), ('test',), ('test1', 'test2'), ['test'], ['test1', 'test2'], [],
            {'test'}, {'test1', 'test2'}
        ]
        invalid_data = [
            ["not_tuple", ValidationError, "Input should be a valid tuple"],
            [123, ValidationError, "Input should be a valid tuple"],
            [12.3, ValidationError, "Input should be a valid tuple"],
            [True, ValidationError, "Input should be a valid tuple"],
            [datetime.now(), ValidationError, "Input should be a valid tuple"],
            [
                {'test key': 'test value'},
                ValidationError,
                "Input should be a valid tuple"
            ],
            [{}, ValidationError, "Input should be a valid tuple"],
            [('test'), ValidationError, "Input should be a valid tuple"],
            [None, ValidationError, "Input should be a valid tuple"]
        ]

        self.create_item(valid_data, invalid_data, "sample_tuple")

    def test_optional_field_validation(self):
        """Test optional field validation"""
        valid_data = ["test_string", None, "123", "", "   Test  "]
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
            [('test1',), ValidationError, "Input should be a valid string"],
            [datetime.now(), ValidationError, "Input should be a valid string"]
        ]

        self.create_item(valid_data, invalid_data, "sample_optional")

    def test_union_field_validation(self):
        """Test union field validation"""
        valid_data = ["test_string", 123, "456", False, 123.00, ('test'), (123)]
        invalid_data = [
            [9.99, ValidationError, "Input should be a valid string"],
            [9.99, ValidationError, "Input should be a valid integer"],
            [['test'], ValidationError, "Input should be a valid string"],
            [['test'], ValidationError, "Input should be a valid integer"],
            [['test1', 'test2'], ValidationError, "Input should be a valid string"],
            [['test1', 'test2'], ValidationError, "Input should be a valid integer"],
            [[], ValidationError, "Input should be a valid string"],
            [[], ValidationError, "Input should be a valid integer"],
            [{'key': 'value'}, ValidationError, "Input should be a valid string"],
            [{'key': 'value'}, ValidationError, "Input should be a valid integer"],
            [{'test'}, ValidationError, "Input should be a valid string"],
            [{'test'}, ValidationError, "Input should be a valid integer"],
            [{'test1', 'test2'}, ValidationError, "Input should be a valid string"],
            [{'test1', 'test2'}, ValidationError, "Input should be a valid integer"],
            [('test1', 'test2'), ValidationError, "Input should be a valid string"],
            [(), ValidationError, "Input should be a valid string"],
            [(), ValidationError, "Input should be a valid integer"],
            [{}, ValidationError, "Input should be a valid string"],
            [{}, ValidationError, "Input should be a valid integer"],
            [('test1',), ValidationError, "Input should be a valid string"],
            [('test1',), ValidationError, "Input should be a valid integer"],
            [datetime.now(), ValidationError, "Input should be a valid string"],
            [datetime.now(), ValidationError, "Input should be a valid integer"],
            [None, ValidationError, "Input should be a valid string"],
            [None, ValidationError, "Input should be a valid integer"]
        ]

        self.create_item(valid_data, invalid_data, "sample_union")

    def test_literal_field_validation(self):
        """Test literal field validation"""
        valid_data = ["test", 25, False, ('test'), (25), (False)]
        invalid_data = [
            ["aa", ValidationError, "Input should be 'test', 25 or False"],
            [123, ValidationError, "Input should be 'test', 25 or False"],
            [True, ValidationError, "Input should be 'test', 25 or False"],
            [9.99, ValidationError, "Input should be 'test', 25 or False"],
            [['test'], ValidationError, "Input should be 'test', 25 or False"],
            [
                ['test1', 'test2'],
                ValidationError,
                "Input should be 'test', 25 or False"
            ],
            [[], ValidationError, "Input should be 'test', 25 or False"],
            [{'key': 'value'}, ValidationError, "Input should be 'test', 25 or False"],
            [{'test'}, ValidationError, "Input should be 'test', 25 or False"],
            [
                ('test1', 'test2'),
                ValidationError,
                "Input should be 'test', 25 or False"
            ],
            [(), ValidationError, "Input should be 'test', 25 or False"],
            [{}, ValidationError, "Input should be 'test', 25 or False"],
            [('test1',), ValidationError, "Input should be 'test', 25 or False"],
            [datetime.now(), ValidationError, "Input should be 'test', 25 or False"],
            [None, ValidationError, "Input should be 'test', 25 or False"]
        ]

        self.create_item(valid_data, invalid_data, "sample_literal")

    def test_email_field_validation(self):
        """Test email field validation"""
        valid_data = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org",
            "123@example.com",
        ]
        invalid_data = [
            [
                "not_an_email",
                ValidationError,
                "value is not a valid email address: An email address must have an "
                "@-sign."
            ],
            [
                "@example.com",
                ValidationError,
                "value is not a valid email address: There must be something before the"
                " @-sign."
            ],
            [
                "test@",
                ValidationError,
                "value is not a valid email address: There must be something after the "
                "@-sign."
            ],
            [
                "test.example.com",
                ValidationError,
                "value is not a valid email address: An email address must have an "
                "@-sign."
            ],
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
            [('test1',), ValidationError, "Input should be a valid string"],
            [datetime.now(), ValidationError, "Input should be a valid string"],
            [None, ValidationError, "Input should be a valid string"]
        ]

        self.create_item(valid_data, invalid_data, "sample_email")

    def test_url_field_validation(self):
        """Test URL field validation"""
        valid_data = [
            "https://example.com",
            "http://example.com",
            "https://example",
            "http://example"
        ]
        invalid_data = [
            [
                "https",
                ValidationError,
                "Input should be a valid URL, relative URL without a base"
            ],
            [
                "http",
                ValidationError,
                "Input should be a valid URL, relative URL without a base"
            ],
            [
                "https://",
                ValidationError,
                "Input should be a valid URL, empty host"
            ],
            [
                "http://",
                ValidationError,
                "Input should be a valid URL, empty host"
            ],
            [
                "aaahttps://example.com",
                ValidationError,
                " URL scheme should be 'http' or 'https'"
            ],
            [
                "not_a_url",
                ValidationError,
                "Input should be a valid URL, relative URL without a base"
            ],
            [
                "example.com",
                ValidationError,
                "Input should be a valid URL, relative URL without a base"
            ],
            [
                "//example.com",
                ValidationError,
                "Input should be a valid URL, relative URL without a base"
            ],
            [123, ValidationError, "URL input should be a string or URL"],
            [12.3, ValidationError, "URL input should be a string or URL"],
            [True, ValidationError, "URL input should be a string or URL"],
            [['test'], ValidationError, "URL input should be a string or URL"],
            [
                ['test1', 'test2'],
                ValidationError,
                "URL input should be a string or URL"
            ],
            [[], ValidationError, "URL input should be a string or URL"],
            [
                {'test1', 'test2'},
                ValidationError,
                "URL input should be a string or URL"
            ],
            [{'test'}, ValidationError, "URL input should be a string or URL"],
            [
                {'test key': 'test value'},
                ValidationError,
                "URL input should be a string or URL"
            ],
            [{}, ValidationError, "URL input should be a string or URL"],
            [
                ('test1', 'test2'),
                ValidationError,
                "URL input should be a string or URL"
            ],
            [(), ValidationError, "URL input should be a string or URL"],
            [('test1',), ValidationError, "URL input should be a string or URL"],
            [datetime.now(), ValidationError, "URL input should be a string or URL"],
            [None, ValidationError, "URL input should be a string or URL"]
        ]

        self.create_item(valid_data, invalid_data, "sample_url")

    def test_decimal_field_validation(self):
        """Test decimal field validation"""
        valid_data = [
            -9999999999.99, 0.0, 88.14, 2025, 9999999999.99, "9999.99", (88.0),
            "9999", Decimal("9999.99"), Decimal("0"), Decimal("-999.99"),
            Decimal("25"), Decimal(25), Decimal(-25)
        ]
        invalid_data = [
            ["test", ValidationError, "Input should be a valid decimal"],
            [
                False,
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                [9999.99],
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                [9999, 9999, 9999],
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                [],
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                {9999.99},
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                {9999.99, 9999.99},
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                {9999.99: 9999.99},
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                {},
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                (9999.99, 9999.99),
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                (),
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                (9999.99,),
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                datetime.now(),
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ],
            [
                None,
                ValidationError,
                "Decimal input should be an integer, float, string or Decimal object"
            ]
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
                (SampleEnum.FIRST,), ValidationError,
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
            [
                None,
                ValidationError,
                "Input should be 'FIRST', 'SECOND' or 'THIRD'"
            ]
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
            [
                (SampleIntEnum.ONE,), ValidationError,
                "Input should be 1, 2 or 3"
            ],
            [(), ValidationError, "Input should be 1, 2 or 3"],
            [
                None,
                ValidationError,
                "Input should be 1, 2 or 3"
            ]
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
                "Input should be a valid dictionary or instance of NestedModel",
            ],
            [
                123,
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                12.3,
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                True,
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                [{'nested_field': 'test', 'nested_number': 42}],
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                [
                    {'nested_field': 'test', 'nested_number': 42},
                    {'nested_field': 'test', 'nested_number': 42}
                ],
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                [],
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                {'test1', 'test2'},
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                {'test1'},
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [{'test key': 'test value'}, ValidationError, "Field required"],
            [{}, ValidationError, "Field required"],
            [
                (
                    {'nested_field': 'test', 'nested_number': 42},
                    {'nested_field': 'test', 'nested_number': 42}
                ),
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                ({'nested_field': 'test', 'nested_number': 42},),
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                (),
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                datetime.now(),
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ],
            [
                None,
                ValidationError,
                "Input should be a valid dictionary or instance of NestedModel"
            ]
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
            "not a path",
            ""
        ]
        invalid_data = [
            [
                123,
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                12.3,
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                True,
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                ['test'],
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                ['test1', 'test2'],
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                [],
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                {'test1', 'test2'},
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                {'test'},
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                {'test key': 'test value'},
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                {},
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                ('test1', 'test2'),
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                ('test1',),
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                (),
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                datetime.now(),
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ],
            [
                None,
                ValidationError,
                "Input is not a valid path for <class 'pathlib.Path'>"
            ]
        ]

        self.create_item(valid_data, invalid_data, "sample_path")
