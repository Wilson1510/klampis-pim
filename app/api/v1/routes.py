from fastapi import APIRouter

from app.api.v1.endpoints import category_type_endpoint

api_router = APIRouter()

# Include category type endpoints
api_router.include_router(
    category_type_endpoint.router,
    prefix="/category-types",
    tags=["category-types"]
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
