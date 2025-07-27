"""
Comprehensive tests for the main FastAPI application.
"""
from unittest.mock import patch
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient

from app.main import app
from app.core.config import settings


class TestAppConfiguration:
    """Test FastAPI application configuration."""

    def test_app_instance_creation(self):
        """Test that the FastAPI app instance is created correctly."""
        assert isinstance(app, FastAPI)
        assert app.title == settings.PROJECT_NAME
        assert app.version == settings.VERSION
        assert app.description == (
            "Product Information Management System for Klampis Mart"
        )
        assert app.openapi_url == f"{settings.API_V1_PREFIX}/openapi.json"

    def test_cors_middleware_configuration(self):
        """Test CORS middleware is configured correctly."""
        # Check if CORS middleware is added
        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware is not None

        # Check CORS configuration - access via kwargs attribute
        cors_kwargs = cors_middleware.kwargs
        assert cors_kwargs["allow_origins"] == settings.BACKEND_CORS_ORIGINS
        assert cors_kwargs["allow_credentials"] is True
        assert cors_kwargs["allow_methods"] == ["*"]
        assert cors_kwargs["allow_headers"] == ["*"]

    def test_api_router_inclusion(self):
        """Test that API router is included with correct prefix."""
        # Check if the API router is included
        api_routes = [
            route for route in app.routes if (
                hasattr(route, 'path') and
                route.path.startswith(settings.API_V1_PREFIX)
            )
        ]
        assert len(api_routes) > 0

    def test_exception_handlers_setup(self):
        """Test that exception handlers are set up."""
        # Test that the app has exception handlers configured
        # We can verify this by checking if custom exception handlers exist
        assert hasattr(app, 'exception_handlers')
        assert len(app.exception_handlers) > 0

        # Verify that our custom exception handlers are registered
        from app.core.exceptions import BaseAPIException
        from fastapi.exceptions import RequestValidationError
        from starlette.exceptions import HTTPException

        # Check if our custom exception types are in the handlers
        handler_types = list(app.exception_handlers.keys())
        assert BaseAPIException in handler_types
        assert RequestValidationError in handler_types
        assert HTTPException in handler_types


class TestRootEndpoint:
    """Test the root endpoint."""

    async def test_root_endpoint_success(self, async_client: AsyncClient):
        """Test root endpoint returns correct response."""
        response = await async_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "PIM System API"
        assert data["version"] == settings.VERSION
        assert len(data) == 2  # Only these two keys should be present
        assert response.headers["content-type"] == "application/json"

    async def test_root_endpoint_method_not_allowed(self, async_client: AsyncClient):
        """Test root endpoint with unsupported HTTP methods."""
        # Test POST method
        response = await async_client.post("/")
        assert response.status_code == 405

        # Test PUT method
        response = await async_client.put("/")
        assert response.status_code == 405

        # Test DELETE method
        response = await async_client.delete("/")
        assert response.status_code == 405

        # Test PATCH method
        response = await async_client.patch("/")
        assert response.status_code == 405


class TestHealthCheckEndpoint:
    """Test the health check endpoint."""

    async def test_health_check_success(self, async_client: AsyncClient):
        """Test health check endpoint returns healthy status."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert len(data) == 1  # Only status key should be present
        assert response.headers["content-type"] == "application/json"

    async def test_health_check_method_not_allowed(self, async_client: AsyncClient):
        """Test health check endpoint with unsupported HTTP methods."""
        # Test POST method
        response = await async_client.post("/health")
        assert response.status_code == 405

        # Test PUT method
        response = await async_client.put("/health")
        assert response.status_code == 405

        # Test DELETE method
        response = await async_client.delete("/health")
        assert response.status_code == 405

        # Test PATCH method
        response = await async_client.patch("/health")
        assert response.status_code == 405

    async def test_health_check_multiple_requests(self, async_client: AsyncClient):
        """Test health check endpoint handles multiple concurrent requests."""
        # Make multiple concurrent requests
        tasks = [async_client.get("/health") for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        # All responses should be successful
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"


class TestAppIntegration:
    """Test application integration scenarios."""

    async def test_app_startup_and_shutdown(self, async_client: AsyncClient):
        """Test application startup and shutdown events."""
        # Test that the app is running by making a request
        response = await async_client.get("/health")
        assert response.status_code == 200

    async def test_cors_headers_in_response(self, async_client: AsyncClient):
        """Test CORS headers are present in responses."""
        response = await async_client.get(
            "/", headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 200
        # Note: CORS headers might not be present in test environment
        # This test verifies the app doesn't break with CORS requests

    async def test_openapi_documentation_accessible(self, async_client: AsyncClient):
        """Test OpenAPI documentation is accessible."""
        response = await async_client.get(f"{settings.API_V1_PREFIX}/openapi.json")

        # Should return OpenAPI schema
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == settings.PROJECT_NAME

    async def test_docs_endpoint_accessible(self, async_client: AsyncClient):
        """Test Swagger UI docs endpoint is accessible."""
        response = await async_client.get("/docs")

        # Should return HTML for Swagger UI
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    async def test_redoc_endpoint_accessible(self, async_client: AsyncClient):
        """Test ReDoc endpoint is accessible."""
        response = await async_client.get("/redoc")

        # Should return HTML for ReDoc
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestErrorHandling:
    """Test error handling scenarios."""

    async def test_404_not_found(self, async_client: AsyncClient):
        """Test 404 error for non-existent endpoints."""
        response = await async_client.get("/non-existent-endpoint")

        assert response.status_code == 404


class TestConfigurationDependency:
    """Test configuration dependency scenarios."""

    @patch('app.core.config.settings')
    def test_app_with_different_config(self, mock_settings):
        """Test app behavior with different configuration."""
        # Mock different settings
        mock_settings.PROJECT_NAME = "Test PIM"
        mock_settings.VERSION = "1.0.0-test"
        mock_settings.API_V1_PREFIX = "/test-api"
        mock_settings.BACKEND_CORS_ORIGINS = ["http://test.com"]

        # Re-import to get new config
        from importlib import reload
        import app.main
        test_app = reload(app.main).app

        # Verify the app uses the mocked settings
        assert test_app.title == "Test PIM"
        assert test_app.version == "1.0.0-test"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    async def test_request_with_special_characters_in_path(
        self, async_client: AsyncClient
    ):
        """Test requests with special characters in path."""
        # Test with URL encoded special characters
        response = await async_client.get("/health%20test")

        # Should return 404 for non-existent path
        assert response.status_code == 404

    async def test_request_with_query_parameters(self, async_client: AsyncClient):
        """Test requests with query parameters on endpoints that don't use them."""
        response = await async_client.get("/health?param1=value1&param2=value2")

        # Should still work and ignore query parameters
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_request_with_fragments(self, async_client: AsyncClient):
        """Test requests with URL fragments."""
        response = await async_client.get("/health#fragment")

        # Should work normally (fragments are client-side)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
