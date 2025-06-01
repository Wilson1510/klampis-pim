from fastapi import APIRouter

from app.api.v1.endpoints import *

api_router = APIRouter()

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