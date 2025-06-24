import uuid

from sqlalchemy import select
from sqlalchemy import exc
from sqlalchemy.types import Boolean, String, Integer
import pytest


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


async def save_object(session, object):
    """
    Save an object to the database.
    """
    session.add(object)
    await session.commit()
    await session.refresh(object)
    return object


async def get_object_by_id(session, model_class, object_id):
    """
    Get an object from the database.
    """
    result = await session.execute(
        select(model_class).where(model_class.id == object_id)
    )
    return result.scalar_one_or_none()


async def get_all_objects(session, model_class):
    """
    Get all objects from the database.
    """
    result = await session.execute(select(model_class))
    return result.scalars().all()


async def delete_object(session, object):
    """
    Delete an object from the database.
    """
    await session.delete(object)
    await session.commit()
    return object


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
