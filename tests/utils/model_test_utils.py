from sqlalchemy import select, func


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
    return await session.get(model_class, object_id)


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


async def count_model_objects(session, model_class):
    """
    Count the number of objects in the database for a given model class.
    """
    result = await session.execute(select(func.count()).select_from(model_class))
    return result.scalar_one()
