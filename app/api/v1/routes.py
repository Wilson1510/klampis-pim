"""
Main API router for version 1.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import *

api_router = APIRouter()

# Include all endpoint routers