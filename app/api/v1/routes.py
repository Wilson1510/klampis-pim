from fastapi import APIRouter, Depends

from app.api.v1.endpoints import (
    auth_endpoint,
    user_endpoint,
    attribute_endpoint,
    category_type_endpoint,
    category_endpoint,
    pricelist_endpoint,
    supplier_endpoint,
    product_endpoint,
    sku_endpoint
)
from app.api.v1.dependencies.auth import get_current_user

# Public router (no authentication required)
public_router = APIRouter()

# Protected router (authentication required)
protected_router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

# Include authentication endpoints (public - no auth required)
public_router.include_router(
    auth_endpoint.router,
    prefix="/auth",
    tags=["authentication"]
)

# Include protected endpoints (authentication required)
protected_router.include_router(
    user_endpoint.router,
    prefix="/users",
    tags=["users"]
)

protected_router.include_router(
    attribute_endpoint.router,
    prefix="/attributes",
    tags=["attributes"]
)

protected_router.include_router(
    category_type_endpoint.router,
    prefix="/category-types",
    tags=["category-types"]
)

protected_router.include_router(
    category_endpoint.router,
    prefix="/categories",
    tags=["categories"]
)

protected_router.include_router(
    pricelist_endpoint.router,
    prefix="/pricelists",
    tags=["pricelists"]
)

protected_router.include_router(
    supplier_endpoint.router,
    prefix="/suppliers",
    tags=["suppliers"]
)

protected_router.include_router(
    product_endpoint.router,
    prefix="/products",
    tags=["products"]
)

protected_router.include_router(
    sku_endpoint.router,
    prefix="/skus",
    tags=["skus"]
)

# Main API router - combine public and protected routers
api_router = APIRouter()
api_router.include_router(public_router)
api_router.include_router(protected_router)
