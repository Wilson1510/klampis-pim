import re
from datetime import datetime


class FieldValidationMixin:
    """
    Mixin class that provides field validation methods for SQLAlchemy models.
    - These validation methods are used to prevent invalid data from being
    inserted into the database that cannot be handled by the database
    constraints.
    - Sometimes the database allows invalid data to be inserted and force to
    convert the data to the correct type like 1 (int) to True (bool).
    - Beside these, the custom validation is also used to prevent some
    characters in string fields like starting with a number or non-alphanumeric
    characters.

    Include this mixin in your SQLAlchemy models to get access to string
    validation methods that can be used with the @validates decorator.
    """

    def validate_string(self, field, value):
        """
        Validates a string field to ensure it:
        - Is trimmed of whitespace
        - Is not empty
        - Does not start with a number
        - Contains only alphanumeric characters and spaces

        Returns:
            The validated string (trimmed)

        Raises:
            ValueError: If the string is empty or contains disallowed
                        characters
            TypeError: If the string starts with a number
        """
        if value is None or not isinstance(value, str):
            return value

        value = value.strip()

        if value == "":
            raise ValueError("Value cannot be empty")

        if value[0].isdigit():
            raise TypeError("Value cannot start with a number")

        if not re.match(r'^[A-Za-z0-9\s]+$', value):
            raise ValueError(
                "Value must contain only alphanumeric characters and spaces"
            )

        return value

    def validate_integer(self, field, value):
        """
        Validates an integer field to ensure it is an integer value.

        Returns:
            The validated integer value

        Raises:
            ValueError: If the value is not an integer
        """
        if value is None:
            return value

        elif not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(
                "Value must be an integer, got %s" % type(value).__name__
            )

        return value

    def validate_boolean(self, field, value):
        """
        Validates a boolean field to ensure it is a boolean value.

        Returns:
            The validated boolean value

        Raises:
            ValueError: If the value is not a boolean
        """
        if value is None:
            return value

        elif not isinstance(value, bool):
            raise TypeError(
                "Value must be a boolean, got %s" % type(value).__name__
            )

        return value

    def validate_datetime(self, field, value):
        """
        Validates datetime object or string to datetime object.

        Returns:
            Datetime object

        Raises:
            TypeError: If the value is not a datetime or valid string
            ValueError: If the string cannot be parsed as a datetime
        """
        # If already a datetime object, use it directly
        # But if the value is None, return the actual value as it will be
        # handled by the database
        if value is None or isinstance(value, datetime):
            return value

        if isinstance(value, str):
            value = value.strip()
            if value == "":
                raise ValueError("Datetime string cannot be empty")

            # Try to parse various input formats
            formats = [
                "%Y-%m-%d %H:%M:%S.%f%z",    # 2025-06-02 23:20:35.661597+08
                "%Y-%m-%d %H:%M:%S.%f+%z",   # 2025-06-02 23:20:35.661597+0800
                "%Y-%m-%d %H:%M:%S%z",       # 2025-06-02 23:20:35+08
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

            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            # If none of the formats work, raise an error
            raise ValueError(f"Invalid datetime format: {value}")

        raise TypeError(
            f"Value must be a datetime object or string, got {type(value).__name__}"
        )
