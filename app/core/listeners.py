from datetime import datetime
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
from app.models.attribute_set_model import AttributeSets
from app.models.pricelist_model import Pricelists
from app.core.security import hash_password
from slugify import slugify


def _truncate_constraint_name(name: str, max_length: int = 63) -> str:
    """
    Truncate constraint name to fit within PostgreSQL's identifier length limit.

    PostgreSQL has a maximum identifier length of 63 characters.
    If the name exceeds this limit, we'll truncate it intelligently.
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


def _validate_all_types_on_save(mapper, connection, target):
    """
    Listener that is called before INSERT or UPDATE.
    Additional validation for String, Integer, Boolean, Float, and DateTime types
    on the 'target' object due to SQLAlchemy doesn't validate the data
    type in some cases.
    """
    # Get class from target object (e.g., User class)
    model_class = target.__class__

    # Collect all columns that already have @validates manual validators
    # Password must not be validated here because it must be saved as it is
    existing_manual_validates = {'password'}

    # Check for validators in the class and its MRO (Method Resolution Order)
    for cls in model_class.__mro__:
        if hasattr(cls, '__mapper__'):
            # Get all validators from the mapper
            if hasattr(cls.__mapper__, 'validators'):
                existing_manual_validates.update(cls.__mapper__.validators.keys())

    for column in target.__table__.columns:
        # Skip columns that have manual validators
        if column.key in existing_manual_validates:
            continue

        value = getattr(target, column.key)

        if value is None:
            continue

        # Validation for String type
        if isinstance(column.type, String) and isinstance(value, str):
            # Trim whitespace and set the value
            value = value.strip()
            setattr(target, column.key, value)

            if value == "":
                if column.nullable is True:
                    continue
                raise ValueError(f"Column '{column.key}' cannot be empty.")

            if 'email' in column.key.lower():
                if '@' not in value:
                    raise ValueError(f"Column '{column.key}' must contain '@'.")
                if '@' in [value[0], value[-1]]:
                    raise ValueError(
                        f"Column '{column.key}' must not start or end with '@'"
                    )
                setattr(target, column.key, value.lower())
                continue

            phone_patterns = [
                'contact', 'phone', 'mobile', 'telp'
            ]

            if any(pattern in column.key.lower() for pattern in phone_patterns):
                if not value.isdigit():
                    raise ValueError(f"Column '{column.key}' must contain only digits.")
                continue

            if isinstance(column.type, Text):
                continue

            if not re.match(r'^[A-Za-z]', value[0]):
                raise ValueError(f"Column '{column.key}' must start with a letter.")

            if not re.match(r'^[A-Za-z0-9\s_-]+$', value):
                raise ValueError(
                    f"Column '{column.key}' can only contain "
                    "alphabet letters, numbers, underscores, and spaces."
                )

        # Validation for Integer type
        elif isinstance(column.type, Integer):
            if isinstance(value, int) and isinstance(value, bool):
                raise TypeError(
                    f"Column '{column.key}' must be an integer, not a boolean."
                )
            if isinstance(value, float):
                raise TypeError(
                    f"Column '{column.key}' must be an integer, not a float."
                )

        # Validation for Boolean type
        elif isinstance(column.type, Boolean):
            # These values will be converted to boolean by SQLAlchemy so we need to
            # prevent it
            problematic_values = [0, 1, 0.0, 1.0]
            if value in problematic_values and not isinstance(value, bool):
                raise TypeError(
                    f"Column '{column.key}' must be a boolean, not "
                    f"{type(value).__name__}."
                )

        # Validation for Float and Numeric types
        elif isinstance(column.type, (Float, Numeric)):
            if isinstance(value, bool):
                raise TypeError(
                    f"Column '{column.key}' must be a float, not a boolean."
                )

        # Validation for Integer and Numeric types - AUTOMATIC positive validation
        elif isinstance(column.type, (Integer, Float, Numeric)):
            # Auto-detect positive columns based on common patterns
            positive_patterns = ['quantity', 'minimum_', 'price']

            if any(pattern in column.key.lower() for pattern in positive_patterns):
                if isinstance(value, (int, float)) and value <= 0:
                    raise ValueError(
                        f"Column '{column.key}' must be a positive number "
                        "(greater than 0)."
                    )

        elif isinstance(column.type, DateTime):
            # There are certain string values that can be converted to datetime
            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    raise ValueError(f"Column '{column.key}' cannot be empty.")

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
                        setattr(target, column.key, datetime.strptime(value, fmt))
                        match = True
                        break
                    except ValueError:
                        continue

                if not match:
                    raise ValueError(f"Invalid datetime format: {value}")


def _apply_automatic_constraints(target, connection, **kw):
    """
    Event listener that automatically applies database constraints
    based on column names and types when table is created.
    """
    # Target is MetaData, iterate through all tables
    for table in target.tables.values():
        _apply_constraints_to_table(table)


def _apply_constraints_to_table(table):
    """
    Apply automatic constraints to a single table.
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

        # Skip system columns
        system_columns = {
            'id', 'created_at', 'updated_at', 'created_by',
            'updated_by', 'is_active', 'sequence'
        }

        # Skip columns that already have explicit constraints or should be excluded
        excluded_columns = {'password', 'last_login'}

        if column_name in system_columns or column_name in excluded_columns:
            continue

        # Check if this column already has constraints defined
        column_constraint_prefixes = [
            f'check_{table_name}_{column_name}_',
            f'{table_name}_{column_name}_'
        ]

        has_existing_constraints = any(
            any(prefix in constraint_name for prefix in column_constraint_prefixes)
            for constraint_name in existing_constraint_names
        )

        if has_existing_constraints:
            continue

        # Handle Enum and Text columns first (no constraints needed)
        if isinstance(column_type, (Enum, Text)):
            # Enum is part of String type but does not have TRIM which causes error.
            # Text does not need character validation constraints.
            continue

        # Handle String columns
        elif isinstance(column_type, String):
            # Email constraints - auto-detect
            if column.nullable is False:
                constraints_to_add.extend([
                    CheckConstraint(
                        f"LENGTH(TRIM({column_name})) > 0",
                        name=_truncate_constraint_name(
                            f'check_{table_name}_{column_name}_not_empty'
                        )
                    )
                ])

            if 'email' in column_name.lower():
                constraints_to_add.extend([
                    CheckConstraint(
                        f"{column_name} ~ '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$'",
                        name=_truncate_constraint_name(
                            f'check_{table_name}_{column_name}_format'
                        )
                    )
                ])

            else:
                constraints_to_add.extend([
                    CheckConstraint(
                        f"{column_name} ~ '^[A-Za-z0-9_ -]*$'",
                        name=_truncate_constraint_name(
                            f'check_{table_name}_{column_name}_valid_chars'
                        )
                    )
                ])

            # Phone/contact constraints - auto-detect
            phone_patterns = ['contact', 'phone', 'mobile', 'telp']
            phone_match = any(
                pattern in column_name.lower() for pattern in phone_patterns
            )
            if phone_match:
                constraints_to_add.extend([
                    CheckConstraint(
                        f"{column_name} ~ '^[0-9]+$'",
                        name=_truncate_constraint_name(
                            f'check_{table_name}_{column_name}_digits_only'
                        )
                    )
                ])
            else:
                # Apply general string validation constraints for non-phone fields
                constraints_to_add.extend([
                    CheckConstraint(
                        f"{column_name} ~ '^[A-Za-z].*'",
                        name=_truncate_constraint_name(
                            f'check_{table_name}_{column_name}_starts_with_letter'
                        )
                    ),
                ])

        # Handle Numeric columns
        elif isinstance(column_type, (Integer, Numeric, Float)):
            # Positive number constraints - auto-detect
            positive_patterns = ['price', 'quantity', 'minimum_']
            positive_match = any(
                pattern in column_name.lower() for pattern in positive_patterns
            )
            if positive_match:
                constraints_to_add.append(
                    CheckConstraint(
                        f"{column_name} > 0",
                        name=_truncate_constraint_name(
                            f'check_{table_name}_{column_name}_positive'
                        )
                    )
                )

    # Add all constraints to the table
    for constraint in constraints_to_add:
        # Check if constraint with same name already exists
        existing_names = [
            c.name for c in table.constraints if hasattr(c, 'name') and c.name
        ]
        if constraint.name not in existing_names:
            table.append_constraint(constraint)


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
    event.listen(AttributeSets.name, 'set', _set_slug)

    event.listen(Attributes.name, 'set', _set_code)
    event.listen(Pricelists.name, 'set', _set_code)
