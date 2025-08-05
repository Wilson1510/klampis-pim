from datetime import datetime
from typing import Any, Set
import re

from sqlalchemy import (
    event, String, Integer, Boolean, DateTime, Float, Text, Numeric, Enum,
    CheckConstraint
)
from sqlalchemy.orm.attributes import get_history

from app.core.base import Base
from app.models.category_type_model import CategoryTypes
from app.models.category_model import Categories
from app.models.supplier_model import Suppliers
from app.models.product_model import Products
from app.models.sku_model import Skus
from app.models.user_model import Users
from app.models.attribute_model import Attributes
from app.models.pricelist_model import Pricelists
from app.core.security import hash_password
from slugify import slugify


# Validation patterns configuration
VALIDATION_PATTERNS = {
    'email': ['email'],  # Original only checked 'email' in column name
    'phone': ['contact', 'phone', 'mobile', 'telp'],  # Same as original
    'positive': ['quantity', 'minimum_', 'price'],  # Same as original
    'non_negative': ['sequence']  # Same as original
}


class BaseValidator:
    """Base validator class with common functionality."""
    pass


class StringValidator(BaseValidator):
    """Handles validation for String and Text columns"""

    @staticmethod
    def validate(target, column, value: str) -> str:
        """Validate string column value"""
        column_key = column.key

        # Trim whitespace and set the value
        value = value.strip()
        setattr(target, column_key, value)

        # Check for empty string
        if value == "":
            if column.nullable is True:
                return value
            raise ValueError(f"Column '{column_key}' cannot be empty.")

        # Email validation
        email_patterns = VALIDATION_PATTERNS['email']
        if any(pattern in column_key.lower() for pattern in email_patterns):
            if '@' not in value:
                raise ValueError(f"Column '{column_key}' must contain '@'.")
            if '@' in [value[0], value[-1]]:
                raise ValueError(
                    f"Column '{column_key}' must not start or end with '@'"
                )
            setattr(target, column_key, value.lower())
            return value

        # Phone validation
        phone_patterns = VALIDATION_PATTERNS['phone']
        if any(pattern in column_key.lower() for pattern in phone_patterns):
            if not value.isdigit():
                raise ValueError(
                    f"Column '{column_key}' must contain only digits."
                )
            return value

        # Text type check
        if isinstance(column.type, Text):
            return value

        # General string validation
        if not re.match(r'^[A-Za-z]', value[0]):
            raise ValueError(f"Column '{column_key}' must start with a letter.")

        if not re.match(r'^[A-Za-z0-9\s_-]+$', value):
            raise ValueError(
                f"Column '{column_key}' can only contain "
                "alphabet letters, numbers, underscores, and spaces."
            )

        return value


class NumericValidator(BaseValidator):
    """Handles validation for Integer, Float, and Numeric columns."""

    @staticmethod
    def validate_integer(target, column, value: Any) -> None:
        """Validate integer column value"""
        column_key = column.key

        if isinstance(value, bool):
            raise TypeError(
                f"Column '{column_key}' must be an integer, not a boolean."
            )
        if isinstance(value, float):
            raise TypeError(
                f"Column '{column_key}' must be an integer, not a float."
            )

    @staticmethod
    def validate_float_numeric(target, column, value: Any) -> None:
        """Validate float or numeric column value"""
        column_key = column.key

        if isinstance(value, bool):
            raise TypeError(
                f"Column '{column_key}' must be a float or numeric, "
                "not a boolean."
            )

    @staticmethod
    def validate_positive_number(target, column, value: Any) -> None:
        """Consolidated positive number validation for all numeric types."""
        column_key = column.key

        # Auto-detect positive columns
        positive_patterns = VALIDATION_PATTERNS['positive']

        if any(pattern in column_key.lower() for pattern in positive_patterns):
            if isinstance(value, (int, float)) and value <= 0:
                raise ValueError(
                    f"Column '{column_key}' must be a positive number "
                    "(greater than 0)."
                )

    @staticmethod
    def validate_non_negative_number(target, column, value: Any) -> None:
        """Validate non-negative number column value"""
        column_key = column.key

        # Auto-detect non-negative columns
        non_negative_patterns = VALIDATION_PATTERNS['non_negative']

        if any(pattern in column_key.lower() for pattern in non_negative_patterns):
            if isinstance(value, (int, float)) and value < 0:
                raise ValueError(
                    f"Column '{column_key}' must be a non-negative number "
                    "(greater than or equal to 0)."
                )


class BooleanValidator(BaseValidator):
    """Handles validation for Boolean columns"""

    @staticmethod
    def validate(target, column, value: Any) -> None:
        """Validate boolean column value"""
        column_key = column.key

        problematic_values = [0, 1, 0.0, 1.0]
        if value in problematic_values and not isinstance(value, bool):
            raise TypeError(
                f"Column '{column_key}' must be a boolean, not "
                f"{type(value).__name__}."
            )


class DateTimeValidator(BaseValidator):
    """Handles validation for DateTime columns"""

    @staticmethod
    def validate(target, column, value: str) -> None:
        """Validate datetime column value"""
        column_key = column.key

        value = value.strip()
        if value == "":
            raise ValueError(f"Column '{column_key}' cannot be empty.")

        # Try to parse various input formats
        formats = [
            "%Y-%m-%d %H:%M:%S.%f%z",    # 2025-06-02 23:20:35.661597+08
            "%Y-%m-%d %H:%M:%S.%f+%z",   # 2025-06-02 23:20:35.661597+0800
            "%Y-%m-%d %H:%M:%S.%f",      # 2025-06-02 23:20:35.661597
            "%Y-%m-%d %H:%M:%S",         # 2023-12-25 14:30:00
            "%Y-%m-%dT%H:%M:%S",         # 2023-12-25T14:30:00 (ISO format)
            "%Y-%m-%dT%H:%M:%SZ",        # 2023-12-25T14:30:00Z (UTC)
            "%Y-%m-%dT%H:%M:%S.%f",      # 2023-12-25T14:30:00.123456
            "%Y-%m-%dT%H:%M:%S.%fZ",     # 2023-12-25T14:30:00.123456Z
            "%Y-%m-%dT%H:%M:%S.%f%z",    # 2023-12-25T14:30:00.123456+01:00
            "%Y-%m-%dT%H:%M:%S%z",       # 2023-12-25T14:30:00+01:00
            "%Y-%m-%d",                  # 2023-12-25 (date only)
        ]

        match = False
        for fmt in formats:
            try:
                setattr(target, column_key, datetime.strptime(value, fmt))
                match = True
                break
            except ValueError:
                continue

        if not match:
            raise ValueError(f"Invalid datetime format: {value}")


def _get_excluded_columns_refactored(model_class) -> Set[str]:
    """Get columns that should be excluded from validation"""
    excluded_columns = {'password'}

    # Check for validators in the class and its MRO (Method Resolution Order)
    for cls in model_class.__mro__:
        if hasattr(cls, '__mapper__'):
            # Get all validators from the mapper
            if hasattr(cls.__mapper__, 'validators'):
                excluded_columns.update(cls.__mapper__.validators.keys())

    return excluded_columns


def _validate_all_types_on_save(mapper, connection, target):
    """
    Listener that is called before INSERT or UPDATE.
    Additional validation for String, Integer, Boolean, Float, and DateTime types
    on the 'target' object due to SQLAlchemy doesn't validate the data
    type in some cases.
    """
    # Get class from target object (e.g., User class)
    model_class = target.__class__

    # Get excluded columns
    excluded_columns = _get_excluded_columns_refactored(model_class)

    for column in target.__table__.columns:
        # Skip columns that have manual validators
        if column.key in excluded_columns:
            continue

        value = getattr(target, column.key)

        # Skip None values
        if value is None:
            continue

        # Route to appropriate validator based on column type

        # Validation for String type
        if isinstance(column.type, String) and isinstance(value, str):
            StringValidator.validate(target, column, value)

        # Validation for Integer type
        elif isinstance(column.type, Integer):
            NumericValidator.validate_integer(target, column, value)
            NumericValidator.validate_positive_number(target, column, value)
            NumericValidator.validate_non_negative_number(target, column, value)

        # Validation for Boolean type
        elif isinstance(column.type, Boolean):
            BooleanValidator.validate(target, column, value)

        # Validation for Float and Numeric types
        elif isinstance(column.type, (Float, Numeric)):
            NumericValidator.validate_float_numeric(target, column, value)
            NumericValidator.validate_positive_number(target, column, value)
            NumericValidator.validate_non_negative_number(target, column, value)

        # Validation for DateTime type
        elif isinstance(column.type, DateTime):
            # There are certain string values that can be converted to datetime
            if isinstance(value, str):
                DateTimeValidator.validate(target, column, value)


def _truncate_constraint_name_refactored(name: str, max_length: int = 63) -> str:
    """
    Truncate constraint name to fit within PostgreSQL's identifier length limit.
    """
    if len(name) <= max_length:
        return name

    # Try to preserve the most important parts: prefix, table, column, suffix
    parts = name.split('_')
    if len(parts) < 4:
        # Simple truncation if we can't parse the structure
        return name[:max_length]

    prefix = parts[0]  # 'check'
    table_part = parts[1]
    column_part = parts[2]
    suffix_parts = parts[3:]
    suffix = '_'.join(suffix_parts)

    # Calculate available space for table and column names
    fixed_parts_length = len(prefix) + len(suffix) + 3  # 3 underscores
    available_space = max_length - fixed_parts_length

    if available_space <= 0:
        # Fallback: just truncate the whole name
        return name[:max_length]

    # Distribute available space between table and column (favor column name)
    if len(table_part) + len(column_part) <= available_space:
        return name  # No truncation needed

    # Truncate table name first, then column name if needed
    table_max = min(len(table_part), available_space // 2)
    column_max = available_space - table_max

    if column_max < 3:  # Ensure column name has at least 3 characters
        table_max = available_space - 3
        column_max = 3

    truncated_table = table_part[:table_max]
    truncated_column = column_part[:column_max]

    return f"{prefix}_{truncated_table}_{truncated_column}_{suffix}"


class DatabaseConstraintValidator:
    """Handles database constraint generation"""

    # System columns that should be skipped
    SYSTEM_COLUMNS = {
        'id', 'created_at', 'updated_at', 'created_by',
        'updated_by', 'is_active', 'sequence'
    }

    # Excluded columns
    EXCLUDED_COLUMNS = {'password'}

    @staticmethod
    def should_skip_column(column_name: str) -> bool:
        """Check if column should be skipped"""
        return (
            column_name in DatabaseConstraintValidator.SYSTEM_COLUMNS
            or column_name in DatabaseConstraintValidator.EXCLUDED_COLUMNS
        )

    @staticmethod
    def has_existing_constraints(
        column_name: str,
        table_name: str,
        existing_constraint_names: list
    ) -> bool:
        """Check if column already has constraints"""
        column_constraint_prefixes = [
            f'check_{table_name}_{column_name}_',
            f'{table_name}_{column_name}_'
        ]

        return any(
            any(
                prefix in constraint_name for prefix in column_constraint_prefixes
            )
            for constraint_name in existing_constraint_names
        )


class StringConstraintGenerator:
    """Generates database constraints for String columns"""

    @staticmethod
    def _detect_column_type(column_name: str) -> str:
        """Detect column type with priority-based matching"""
        # Email has higher priority than phone for mixed cases
        email_patterns = VALIDATION_PATTERNS['email']
        if any(pattern in column_name.lower() for pattern in email_patterns):
            return 'email'

        phone_patterns = VALIDATION_PATTERNS['phone']
        if any(pattern in column_name.lower() for pattern in phone_patterns):
            return 'phone'

        return 'general'

    @staticmethod
    def generate_constraints(column, table_name: str) -> list:
        """Generate string constraints"""
        constraints_to_add = []
        column_name = column.name

        # 1. Not empty constraint (independent of type)
        if column.nullable is False:
            constraints_to_add.extend([
                CheckConstraint(
                    f"LENGTH(TRIM({column_name})) > 0",
                    name=_truncate_constraint_name_refactored(
                        f'check_{table_name}_{column_name}_not_empty'
                    )
                )
            ])

        # 2. Format-specific constraints (mutually exclusive)
        column_type = StringConstraintGenerator._detect_column_type(column_name)

        if column_type == 'email':
            # Email-specific constraints only
            constraints_to_add.extend([
                CheckConstraint(
                    f"{column_name} LIKE '%@%' AND {column_name} NOT LIKE"
                    f" '@%' AND {column_name} NOT LIKE '%@'",
                    # f"{column_name} ~ '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$'",
                    name=_truncate_constraint_name_refactored(
                        f'check_{table_name}_{column_name}_format'
                    )
                )
            ])

        elif column_type == 'phone':
            # Phone-specific constraints only
            constraints_to_add.extend([
                CheckConstraint(
                    f"{column_name} ~ '^[0-9]+$'",
                    name=_truncate_constraint_name_refactored(
                        f'check_{table_name}_{column_name}_digits_only'
                    )
                )
            ])

        else:
            # General string constraints (consolidated, no redundancy)
            if column.nullable:
                # Allow empty strings OR valid general format
                constraint_pattern = (
                    f"({column_name} = '' OR "
                    f"{column_name} ~ '^[A-Za-z][A-Za-z0-9_ -]*$')"
                )
            else:
                # Non-nullable: must follow general format
                constraint_pattern = f"{column_name} ~ '^[A-Za-z][A-Za-z0-9_ -]*$'"

            constraints_to_add.extend([
                CheckConstraint(
                    constraint_pattern,
                    name=_truncate_constraint_name_refactored(
                        f'check_{table_name}_{column_name}_valid_format'
                    )
                )
            ])

        return constraints_to_add


class NumericConstraintGenerator:
    """Generates database constraints for Numeric columns"""

    @staticmethod
    def generate_constraints(column, table_name: str) -> list:
        """Generate numeric constraints - consistent with application validator."""
        constraints_to_add = []
        column_name = column.name

        # Use VALIDATION_PATTERNS for positive detection - consistent order
        positive_patterns = VALIDATION_PATTERNS['positive']
        positive_match = any(
            pattern in column_name.lower() for pattern in positive_patterns
        )
        if positive_match:
            constraints_to_add.append(
                CheckConstraint(
                    f"{column_name} > 0",
                    name=_truncate_constraint_name_refactored(
                        f'check_{table_name}_{column_name}_positive'
                    )
                )
            )

        # Use VALIDATION_PATTERNS for non-negative detection - consistent order
        non_negative_patterns = VALIDATION_PATTERNS['non_negative']
        non_negative_match = any(
            pattern in column_name.lower() for pattern in non_negative_patterns
        )
        if non_negative_match:
            constraints_to_add.append(
                CheckConstraint(
                    f"{column_name} >= 0",
                    name=_truncate_constraint_name_refactored(
                        f'check_{table_name}_{column_name}_non_negative'
                    )
                )
            )

        return constraints_to_add


def _apply_constraints_to_table(table):
    """
    Apply automatic constraints to a single table
    """
    constraints_to_add = []
    table_name = table.name

    # Get existing constraint names for this table
    existing_constraint_names = [
        c.name for c in table.constraints if hasattr(c, 'name') and c.name
    ]

    for column in table.columns:
        column_name = column.name
        column_type = column.type

        # Skip system and excluded columns
        if DatabaseConstraintValidator.should_skip_column(column_name):
            continue

        # Check if this column already has constraints
        if DatabaseConstraintValidator.has_existing_constraints(
            column_name, table_name, existing_constraint_names
        ):
            continue

        # Handle Enum and Text columns first
        if isinstance(column_type, (Enum, Text)):
            # Enum is part of String type but does not have TRIM which causes error.
            # Text does not need character validation constraints.
            continue

        # Handle String columns
        elif isinstance(column_type, String):
            string_constraints = StringConstraintGenerator.generate_constraints(
                column, table_name
            )
            constraints_to_add.extend(string_constraints)

        # Handle Numeric columns
        elif isinstance(column_type, (Integer, Numeric, Float)):
            numeric_constraints = NumericConstraintGenerator.generate_constraints(
                column, table_name
            )
            constraints_to_add.extend(numeric_constraints)

    # Add all constraints to the table
    for constraint in constraints_to_add:
        # Check if constraint with same name already exists
        existing_names = [
            c.name for c in table.constraints if hasattr(c, 'name') and c.name
        ]
        if constraint.name not in existing_names:
            table.append_constraint(constraint)


def _apply_automatic_constraints(target, connection, **kw):
    """
    Event listener that automatically applies database constraints
    """
    # Target is MetaData, iterate through all tables
    for table in target.tables.values():
        _apply_constraints_to_table(table)


def _hash_new_password_listener(mapper, connection, target):
    """Listener for hashing password ONLY on User model."""
    # Check if 'password' field is actually changed to avoid re-hashing
    if get_history(target, 'password').has_changes():
        plain_password = target.password
        if plain_password:
            target.password = hash_password(plain_password)


def _set_slug(target, value, oldvalue, initiator):
    """
    Event listener to automatically generate slug from name.

    This event fires before insert and update operations to ensure
    the slug is always generated from the current name value.
    """
    if value is None:
        return

    target.slug = slugify(value)


def _set_code(target, value, oldvalue, initiator):
    """
    Event listener to automatically generate code from name.

    The code is generated from the name by slugifying it and converting it to uppercase.
    """
    if value is None:
        return
    target.code = slugify(value).upper()


def register_listeners():
    """
    Registers all SQLAlchemy event listeners.
    Call this function once during application startup.
    """
    event.listen(Base, 'before_insert', _validate_all_types_on_save, propagate=True)
    event.listen(Base, 'before_update', _validate_all_types_on_save, propagate=True)
    event.listen(
        Base.metadata,
        'before_create',
        _apply_automatic_constraints,
        propagate=True
    )

    event.listen(Users, 'before_insert', _hash_new_password_listener)
    event.listen(Users, 'before_update', _hash_new_password_listener)

    event.listen(CategoryTypes.name, 'set', _set_slug)
    event.listen(Categories.name, 'set', _set_slug)
    event.listen(Suppliers.name, 'set', _set_slug)
    event.listen(Products.name, 'set', _set_slug)
    event.listen(Skus.name, 'set', _set_slug)

    event.listen(Attributes.name, 'set', _set_code)
    event.listen(Pricelists.name, 'set', _set_code)
