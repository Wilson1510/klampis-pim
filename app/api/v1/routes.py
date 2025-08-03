from fastapi import APIRouter

from app.api.v1.endpoints import (
    attribute_endpoint,
    category_type_endpoint,
    category_endpoint,
    supplier_endpoint,
    product_endpoint,
    sku_endpoint
)

api_router = APIRouter()

# Include attribute endpoints
api_router.include_router(
    attribute_endpoint.router,
    prefix="/attributes",
    tags=["attributes"]
)

# Include category type endpoints
api_router.include_router(
    category_type_endpoint.router,
    prefix="/category-types",
    tags=["category-types"]
)

# Include category endpoints
api_router.include_router(
    category_endpoint.router,
    prefix="/categories",
    tags=["categories"]
)

# Include supplier endpoints
api_router.include_router(
    supplier_endpoint.router,
    prefix="/suppliers",
    tags=["suppliers"]
)

# Include product endpoints
api_router.include_router(
    product_endpoint.router,
    prefix="/products",
    tags=["products"]
)

# Include SKU endpoints
api_router.include_router(
    sku_endpoint.router,
    prefix="/skus",
    tags=["skus"]
)

# Import and include other endpoint routers here
# Example:
# from app.api.v1.endpoints import groups, pricelists
# api_router.include_router(
#     groups.router,
#     prefix="/groups",
#     tags=["groups"]
# )
# api_router.include_router(
#     pricelists.router,
#     prefix="/pricelists",
#     tags=["pricelists"]
# )
