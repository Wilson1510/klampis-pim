import re


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
