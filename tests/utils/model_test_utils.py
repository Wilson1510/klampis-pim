import uuid
import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc
from sqlalchemy.types import Boolean, DateTime, String, Integer
import pytest


def assert_tablename_generation(model_class, expected_tablename=None):
    """
    Test that the table name is correctly generated for a given model class.

    Args:
        model_class: SQLAlchemy model class to test
        expected_tablename: Optional expected table name. If not provided,
                          it will be generated based on the class name.
    """
    if expected_tablename is None:
        # Generate expected table name from class name in snake_case
        expected_tablename = ''.join(
            ['_' + c.lower() if c.isupper() else c
             for c in model_class.__name__]
        ).lstrip('_')

    assert model_class.__tablename__ == expected_tablename


def assert_relationship(model_class, relationship_name, back_populates):
    """
    Test a relationship for a given model class.

    Args:
        model_class: SQLAlchemy model class to test
        relationship_name: Name of the relationship to test
        target_attr: Optional name of the target attribute on the related class
        back_populates: Optional name of the back_populates property
    """
    relationship_prop = getattr(model_class, relationship_name)

    assert relationship_prop is not None
    assert relationship_prop.key == relationship_name
    assert relationship_name in model_class.__mapper__.relationships
    assert relationship_prop.property.back_populates == back_populates


def assert_custom_validation(model_class, common_params, target_field):
    """
    Test that an invalid input value for a field raises the correct error based
    on the model's custom validation.

    Args:
        model_class: The model class to create
        common_params: The common parameters to set for the model
        target_field: The field to test
    """
    field_type = model_class.__table__.columns.get(target_field).type

    if isinstance(field_type, String):
        invalid_data = {
            # Integer is not allowed
            12345: (TypeError, None),
            # String starting with number is not allowed
            "12aaqw": (TypeError, "Value cannot start with a number"),
            # Boolean is not allowed
            True: (TypeError, None),
            # Special characters are not allowed
            "Test@Category#Type!": (
                ValueError,
                "Value must contain only alphanumeric characters and spaces"
            ),
            # Empty string is not allowed
            "": (ValueError, "Value cannot be empty"),
            # UUID is not allowed
            uuid.uuid4(): (
                TypeError,
                "decoding to str: need a bytes-like object, UUID found"
            ),
        }
    elif isinstance(field_type, Integer):
        invalid_data = {
            # Float is not allowed
            3.36: (TypeError, "Value must be an integer, got float"),
            # String is not allowed even if it is a digit
            "25": (TypeError, "Value must be an integer, got str"),
            # Boolean is not allowed
            False: (TypeError, "Value must be an integer, got bool"),
            # String is not allowed
            "test": (TypeError, "Value must be an integer, got str"),
            # UUID is not allowed
            uuid.uuid4(): (TypeError, "Value must be an integer, got UUID"),
        }

    elif isinstance(field_type, Boolean):
        invalid_data = {
            0: (TypeError, "Value must be a boolean, got int"),
            # Integer is not allowed even if it can be converted to boolean
            1: (TypeError, "Value must be a boolean, got int"),
            "true": (TypeError, "Value must be a boolean, got str"),
            "false": (TypeError, "Value must be a boolean, got str"),
            "testst": (TypeError, "Value must be a boolean, got str"),
            uuid.uuid4(): (TypeError, "Value must be a boolean, got UUID"),
            # UUID is not allowed
        }

    for invalid_input, expected_error in invalid_data.items():
        object_to_test = common_params.copy()
        object_to_test = {**object_to_test, target_field: invalid_input}

        with pytest.raises(expected_error[0]) as exc_info:
            # Create object with kwargs to delay validation
            model_class(**object_to_test)

        if expected_error[1]:
            assert str(exc_info.value) == expected_error[1]


async def assert_string_field_length(
        model_class,
        common_params,
        target_field,
        session,
        max_length):
    """
    Test that a string field enforces its length constraints, even when model
    has multiple fields of different types.

    Parameters:
    -----------
    model_class : SQLAlchemy model class
        The model class to test

    common_params : dict
        The common parameters to set for the model

    target_field : str
        The name of the string field to test length validation on

    session : AsyncSession
        SQLAlchemy async session for database operations

    max_length : int
        Maximum allowed length for the field. Test will verify that:
        1. A string of exactly this length is accepted
        2. A string longer than this length raises an error

    Raises:
    -------
    AssertionError
        If any of the length validations fail
    """
    # Prepare required fields if provided, otherwise use empty dict

    # Test maximum length
    # String of exactly max_length should be valid
    exact_max = "A" * max_length
    fields_max = {**common_params, target_field: exact_max}

    model_valid_max = model_class(**fields_max)
    session.add(model_valid_max)
    await session.flush()  # This should succeed
    await session.rollback()

    # String longer than max_length should raise error
    too_long = "A" * (max_length + 1)
    fields_too_long = {**common_params, target_field: too_long}

    model_invalid_max = model_class(**fields_too_long)
    session.add(model_invalid_max)

    with pytest.raises(exc.DBAPIError):
        await session.flush()
    await session.rollback()


async def assert_string_whitespace_handling(
        model_class,
        common_params,
        target_field,
        session):
    """
    Test how whitespace in string fields is handled.

    Parameters:
    -----------
    model_class : SQLAlchemy model class
        The model class to test

    field_name : str
        The name of the string field to test whitespace handling

    session : AsyncSession
        SQLAlchemy async session for database operations
    """

    # Create test values with different whitespace patterns
    test_value = "Test String Value"
    both_ws = "   " + test_value + "   "

    # Test leading and trailing whitespace
    params = {**common_params, target_field: both_ws}
    model = model_class(**params)
    await model.save(session)

    # Query the model to see how whitespace was handled
    retrieved_model = await model_class.get_by_id(session, model.id)

    # Check result based on expected behavior
    stored_value = getattr(retrieved_model, target_field)

    assert stored_value == test_value


async def assert_bulk_creation(session, valid_objects, invalid_objects):
    """
    Test bulk creation of models with valid and invalid values.
    """
    item_class = valid_objects[0].__class__
    session.add_all(valid_objects)
    await session.flush()

    count = await item_class.get_count(session)

    assert count == len(valid_objects) + 2

    await session.rollback()

    session.add_all(invalid_objects)

    with pytest.raises(exc.DBAPIError):
        await session.flush()
    await session.rollback()

    count = await item_class.get_count(session)
    assert count == 2


async def assert_data_not_updated_when_rollback(
        session,
        class_model,
        common_params,
        update_param
        ):
    """
    Test that data is not updated when rollback occurs
    """
    # Create a new item
    new_item = class_model(**common_params)
    await new_item.save(session)
    new_id = new_item.id

    # Change a field in memory
    for key, value in update_param.items():
        setattr(new_item, key, value)

    # Rollback without saving
    await session.rollback()

    # Query the database to verify the original data is intact
    result = await class_model.get_by_id(session, new_id)

    assert result is not None

    for key, value in common_params.items():
        if key in update_param:
            assert getattr(result, key) == common_params[key]

    # Now modify and save properly
    for key, value in update_param.items():
        setattr(result, key, value)

    await result.save(session)

    # Query again to verify the change persisted
    updated = await class_model.get_by_id(session, new_id)

    for key, value in update_param.items():
        assert getattr(updated, key) == value


async def assert_rollback_on_error(session, valid_object, invalid_object):
    """
    Test that a transaction is rolled back if an error occurs during bulk
    creation of models with valid and invalid values.
    """
    session.add(valid_object)
    await session.flush()

    with pytest.raises(exc.DBAPIError):
        await invalid_object.save(session)
    await session.rollback()

    model = await valid_object.__class__.get_by_id(session, valid_object.id)

    assert model is None