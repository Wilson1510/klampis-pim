from fastapi import APIRouter, Depends

from app.api.v1.endpoints import (
    auth_endpoint,
    user_endpoint,
    profile_endpoint,
    attribute_endpoint,
    category_type_endpoint,
    category_endpoint,
    pricelist_endpoint,
    supplier_endpoint,
    product_endpoint,
    sku_endpoint
)
from app.api.v1.dependencies.auth import (
    get_current_user,
    get_current_admin_user,
    get_current_manager_or_admin_user
)

# ============================================================================
# ROUTER GROUPS BY PERMISSION LEVEL
# ============================================================================

# Public router (no authentication required)
public_router = APIRouter()

# Protected router (authentication required - all roles)
# For READ operations and resources with ownership-based protection
protected_router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

# Manager router (ADMIN, MANAGER, SYSTEM roles only)
# For management operations that don't require ownership checks
manager_router = APIRouter(
    dependencies=[Depends(get_current_manager_or_admin_user)]
)

# Admin router (ADMIN role only)
# For admin-only operations like user management
admin_router = APIRouter(
    dependencies=[Depends(get_current_admin_user)]
)

# ============================================================================
# PUBLIC ENDPOINTS (No authentication required)
# ============================================================================

# Authentication endpoints
public_router.include_router(
    auth_endpoint.router,
    prefix="/auth",
    tags=["authentication"]
)

# ============================================================================
# PROTECTED ENDPOINTS (All authenticated users with ownership checks)
# ============================================================================

# User profile management - all users can manage their own profile
protected_router.include_router(
    profile_endpoint.router,
    prefix="/profile",
    tags=["profile"]
)

# Resource endpoints - READ for all, CREATE/UPDATE/DELETE with ownership checks
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

# ============================================================================
# MANAGER ENDPOINTS (ADMIN, MANAGER, SYSTEM roles only)
# ============================================================================

# Future: Add bulk operations, advanced reports, etc. here if needed
# These would be operations that bypass ownership checks

# ============================================================================
# ADMIN ENDPOINTS (ADMIN role only)
# ============================================================================

# User management - only admins can manage other users
admin_router.include_router(
    user_endpoint.router,
    prefix="/users",
    tags=["user-management"]
)

# ============================================================================
# MAIN API ROUTER
# ============================================================================

api_router = APIRouter()

# Include all router groups
api_router.include_router(public_router)
api_router.include_router(protected_router)
api_router.include_router(manager_router, prefix="/manager")
api_router.include_router(admin_router, prefix="/admin")
