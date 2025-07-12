from datetime import datetime
import re

from sqlalchemy import event, String, Integer, Boolean, DateTime, Float, Text
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
from app.core.security import hash_password
from slugify import slugify


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

        # Validation for Float type
        elif isinstance(column.type, Float):
            if isinstance(value, bool):
                raise TypeError(
                    f"Column '{column.key}' must be a float, not a boolean."
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

    event.listen(Users, 'before_insert', _hash_new_password_listener)
    event.listen(Users, 'before_update', _hash_new_password_listener)

    event.listen(CategoryTypes.name, 'set', _set_slug)
    event.listen(Categories.name, 'set', _set_slug)
    event.listen(Suppliers.name, 'set', _set_slug)
    event.listen(Products.name, 'set', _set_slug)
    event.listen(Skus.name, 'set', _set_slug)
    event.listen(AttributeSets.name, 'set', _set_slug)

    event.listen(Attributes.name, 'set', _set_code)
