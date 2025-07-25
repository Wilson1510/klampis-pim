from app.models.category_type_model import CategoryTypes
from app.schemas.category_type_schema import CategoryTypeCreate, CategoryTypeUpdate
from app.repositories.base import CRUDBase


class CategoryTypeRepository(
    CRUDBase[CategoryTypes, CategoryTypeCreate, CategoryTypeUpdate]
):
    """Repository for CategoryType operations."""
    pass


# Create instance to be used as dependency
category_type_repository = CategoryTypeRepository(CategoryTypes)
