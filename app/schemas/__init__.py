# Export base schemas for easy importing
from app.schemas.base import (
    BaseSchema,
    BaseCreateSchema,
    BaseUpdateSchema,
    BaseInDB,
    MetaSchema,
    ErrorDetailSchema,
    SingleItemResponse,
    MultipleItemsResponse,
)

# Export entity schemas
from app.schemas.category_type_schema import (
    CategoryTypeResponse,
    CategoryTypeCreate,
    CategoryTypeUpdate,
    CategoryTypeInDB,
)

from app.schemas.category_schema import (
    CategoryResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryInDB,
)

__all__ = [
    # Base schemas
    "BaseSchema",
    "BaseCreateSchema",
    "BaseUpdateSchema",
    "BaseInDB",
    # Response wrappers
    "MetaSchema",
    "ErrorDetailSchema",
    "SingleItemResponse",
    "MultipleItemsResponse",
    # Entity schemas
    "CategoryTypeResponse",
    "CategoryTypeCreate",
    "CategoryTypeUpdate",
    "CategoryTypeInDB",
    "CategoryResponse",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryInDB",
]
