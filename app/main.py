"""
FastAPI application entry point for the PIM system.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import api_router
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Product Information Management System for Klampis Mart",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Set up exception handlers
setup_exception_handlers(app)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "PIM System API", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
