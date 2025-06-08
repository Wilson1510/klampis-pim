from datetime import datetime
import re

from sqlalchemy import event, String, Integer, Boolean, DateTime, Float, Text

from app.core.base import Base


def validate_all_types_on_save(mapper, connection, target):
    """
    Listener that is called before INSERT or UPDATE.
    Additional validation for String, Integer, Boolean, Float, and DateTime types
    on the 'target' object due to SQLAlchemy doesn't validate the data
    type in some cases.
    """
    for column in target.__table__.columns:
        value = getattr(target, column.key)

        if value is None:
            continue

        # Validation for String type
        if isinstance(column.type, String) and isinstance(value, str):
            # Trim whitespace and set the value
            value = value.strip()
            setattr(target, column.key, value)

            if value == "":
                raise ValueError(f"Column '{column.key}' cannot be empty.")

            if isinstance(column.type, Text):
                continue

            if value[0].isdigit():
                raise ValueError(f"Column '{column.key}' cannot start with a number.")

            if not re.match(r'^[A-Za-z0-9\s]+$', value):
                raise ValueError(
                    f"Column '{column.key}' with value '{value}' can only contain "
                    "alphabet letters and spaces."
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


# Register listener directly in this file.
# This code will be executed when this file is imported.
event.listen(Base, 'before_insert', validate_all_types_on_save, propagate=True)
event.listen(Base, 'before_update', validate_all_types_on_save, propagate=True)
