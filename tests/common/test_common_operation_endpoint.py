"""
Common endpoint operation tests using CategoryType as example.

This module provides comprehensive tests for common CRUD operations
that can be applied to any endpoint following the same patterns.
"""

import asyncio
from httpx import AsyncClient


class TestGetAllModel:
    """Test cases for GET / endpoint with empty data."""

    async def test_get_simple_model_empty_list(self, async_client: AsyncClient):
        """Test getting models when none exist."""
        response = await async_client.get("/api/v1/category-types/")

        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [],
            "meta": {
                "page": 1,
                "limit": 100,
                "total": 0,
                "pages": 0
            },
            "error": None
        }

    async def test_get_simple_model_with_pagination(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test getting models with pagination."""
        # Create 5 category types
        for i in range(5):
            await category_type_factory(name=f"Category Type {i}")

        # Test first page with limit 2
        response = await async_client.get("/api/v1/category-types/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "name": "Category Type 0",
                    "slug": "category-type-0",
                    "is_active": True,
                    "sequence": 0,
                    "created_at": data["data"][0]["created_at"],
                    "updated_at": data["data"][0]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                },
                {
                    "id": 2,
                    "name": "Category Type 1",
                    "slug": "category-type-1",
                    "is_active": True,
                    "sequence": 0,
                    "created_at": data["data"][1]["created_at"],
                    "updated_at": data["data"][1]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                }
            ],
            "meta": {
                "page": 1,
                "limit": 2,
                "total": 2,
                "pages": 1
            },
            "error": None
        }

        # Test second page
        response = await async_client.get("/api/v1/category-types/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [
                {
                    "id": 3,
                    "name": "Category Type 2",
                    "slug": "category-type-2",
                    "is_active": True,
                    "sequence": 0,
                    "created_at": data["data"][0]["created_at"],
                    "updated_at": data["data"][0]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                },
                {
                    "id": 4,
                    "name": "Category Type 3",
                    "slug": "category-type-3",
                    "is_active": True,
                    "sequence": 0,
                    "created_at": data["data"][1]["created_at"],
                    "updated_at": data["data"][1]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                }
            ],
            "meta": {
                "page": 2,
                "limit": 2,
                "total": 2,
                "pages": 1
            },
            "error": None
        }

        # Test last page
        response = await async_client.get("/api/v1/category-types/?skip=4&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [
                {
                    "id": 5,
                    "name": "Category Type 4",
                    "slug": "category-type-4",
                    "is_active": True,
                    "sequence": 0,
                    "created_at": data["data"][0]["created_at"],
                    "updated_at": data["data"][0]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                }
            ],
            "meta": {
                "page": 3,
                "limit": 2,
                "total": 1,
                "pages": 1
            },
            "error": None
        }

    async def test_get_simple_model_pagination_edge_cases(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test pagination edge cases."""
        # Create 3 category types
        for i in range(3):
            await category_type_factory(name=f"Category Type {i}")

        # Test skip beyond available records
        response = await async_client.get("/api/v1/category-types/?skip=10")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [],
            "meta": {
                "page": 1,
                "limit": 100,
                "total": 0,
                "pages": 0
            },
            "error": None
        }

        # Test limit larger than available records
        response = await async_client.get("/api/v1/category-types/?limit=100")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "name": "Category Type 0",
                    "slug": "category-type-0",
                    "is_active": True,
                    "sequence": 0,
                    "created_at": data["data"][0]["created_at"],
                    "updated_at": data["data"][0]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                },
                {
                    "id": 2,
                    "name": "Category Type 1",
                    "slug": "category-type-1",
                    "is_active": True,
                    "sequence": 0,
                    "created_at": data["data"][1]["created_at"],
                    "updated_at": data["data"][1]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                },
                {
                    "id": 3,
                    "name": "Category Type 2",
                    "slug": "category-type-2",
                    "is_active": True,
                    "sequence": 0,
                    "created_at": data["data"][2]["created_at"],
                    "updated_at": data["data"][2]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                }
            ],
            "meta": {
                "page": 1,
                "limit": 100,
                "total": 3,
                "pages": 1
            },
            "error": None
        }

        # Test invalid pagination parameters
        response = await async_client.get("/api/v1/category-types/?skip=-1")
        assert response.status_code == 422
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": [
                    {
                        "loc": ["query", "skip"],
                        "msg": "Input should be greater than or equal to 0",
                        "type": "greater_than_equal"
                    }
                ]
            }
        }

        response = await async_client.get("/api/v1/category-types/?limit=0")
        assert response.status_code == 422
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": [
                    {
                        "loc": ["query", "limit"],
                        "msg": "Input should be greater than or equal to 1",
                        "type": "greater_than_equal"
                    }
                ]
            }
        }

        response = await async_client.get("/api/v1/category-types/?limit=1001")
        assert response.status_code == 422
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": [
                    {
                        "loc": ["query", "limit"],
                        "msg": "Input should be less than or equal to 1000",
                        "type": "less_than_equal"
                    }
                ]
            }
        }


class TestCreateModel:
    """Test cases for POST / endpoint."""

    async def test_create_simple_model_with_all_fields_provided(
        self, async_client: AsyncClient
    ):
        """Test creating model with all fields provided."""
        model_data = {
            "name": "Electronics and Gadgets",
            "is_active": True,
            "sequence": 10
        }

        response = await async_client.post(
            "/api/v1/category-types/",
            json=model_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Electronics and Gadgets",
                "slug": "electronics-and-gadgets",
                "is_active": True,
                "sequence": 10,
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None
        }

    async def test_create_simple_model_with_only_required_fields(
        self, async_client: AsyncClient
    ):
        """Test creating model with only required fields."""
        model_data = {
            "name": "Food and Beverages"
        }

        response = await async_client.post(
            "/api/v1/category-types/",
            json=model_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Food and Beverages",
                "slug": "food-and-beverages",
                "is_active": True,
                "sequence": 0,
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None
        }

    async def test_create_simple_model_with_partial_required(
        self, async_client: AsyncClient
    ):
        """Test creating model with missing required fields."""
        # Missing name (required field)
        model_data = {
            "is_active": True,
            "sequence": 5
        }

        response = await async_client.post(
            "/api/v1/category-types/",
            json=model_data
        )
        assert response.status_code == 422
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": [
                    {
                        "loc": ["body", "name"],
                        "msg": "Field required",
                        "type": "missing"
                    }
                ]
            }
        }

    async def test_create_simple_model_with_only_optional_fields(
        self, async_client: AsyncClient
    ):
        """Test creating model with only optional fields (should fail)."""
        model_data = {
            "is_active": False,
            "sequence": 10
        }

        response = await async_client.post(
            "/api/v1/category-types/",
            json=model_data
        )
        assert response.status_code == 422
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": [
                    {
                        "loc": ["body", "name"],
                        "msg": "Field required",
                        "type": "missing"
                    }
                ]
            }
        }

    async def test_create_simple_model_with_no_fields(
        self, async_client: AsyncClient
    ):
        """Test creating model with no fields provided."""
        response = await async_client.post("/api/v1/category-types/", json={})
        assert response.status_code == 422
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": [
                    {
                        "loc": ["body", "name"],
                        "msg": "Field required",
                        "type": "missing"
                    }
                ]
            }
        }


class TestUpdateModel:
    """Test cases for PUT /{id} endpoint."""

    async def test_update_simple_model_with_all_fields_provided(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test updating model with all fields provided."""
        category_type = await category_type_factory(
            name="Original Name",
            is_active=True,
            sequence=5
        )

        update_data = {
            "name": "Updated Electronics",
            "is_active": False,
            "sequence": 20
        }

        response = await async_client.put(
            f"/api/v1/category-types/{category_type.id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Updated Electronics",
                "slug": "updated-electronics",
                "is_active": False,
                "sequence": 20,
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None
        }

    async def test_update_simple_model_with_no_fields(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test updating model with empty request body."""
        category_type = await category_type_factory(
            name="Original Name",
            sequence=10
        )

        response = await async_client.put(
            f"/api/v1/category-types/{category_type.id}",
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Original Name",
                "slug": "original-name",
                "is_active": True,
                "sequence": 10,
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None
        }

    async def test_update_simple_model_same_name(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test updating model with same name (should succeed)."""
        category_type = await category_type_factory(
            name="Electronics",
            sequence=5
        )

        update_data = {
            "name": "Electronics",  # Same name
            "sequence": 15  # Different sequence
        }

        response = await async_client.put(
            f"/api/v1/category-types/{category_type.id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Electronics",
                "slug": "electronics",
                "is_active": True,
                "sequence": 15,
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None
        }


class TestGetChildrenByModel:
    """Test cases for GET /{id}/children endpoint."""

    async def test_get_children_by_model_empty_list(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test getting children when none exist."""
        category_type = await category_type_factory(name="Electronics")

        response = await async_client.get(
            f"/api/v1/category-types/{category_type.id}/categories/"
        )

        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [],
            "meta": {
                "page": 1,
                "limit": 100,
                "total": 0,
                "pages": 0
            },
            "error": None
        }

    async def test_get_children_by_model_with_pagination(
        self, async_client: AsyncClient, category_type_factory, category_factory
    ):
        """Test getting children with pagination."""
        category_type = await category_type_factory(name="Electronics")

        # Create 5 categories under this category type
        for i in range(5):
            await category_factory(
                name=f"Category {i}",
                category_type=category_type
            )

        # Test first page
        response = await async_client.get(
            f"/api/v1/category-types/{category_type.id}/categories/?skip=0&limit=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "name": "Category 0",
                    "slug": "category-0",
                    "description": None,
                    "parent_id": None,
                    "category_type_id": 1,
                    "is_active": True,
                    "children": [],
                    "full_path": [
                        {
                            "name": "Category 0",
                            "slug": "category-0",
                            "category_type": "Electronics",
                            "type": "Category"
                        }
                    ],
                    "images": [],
                    "sequence": 0,
                    "created_at": data["data"][0]["created_at"],
                    "updated_at": data["data"][0]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                },
                {
                    "id": 2,
                    "name": "Category 1",
                    "slug": "category-1",
                    "description": None,
                    "parent_id": None,
                    "category_type_id": 1,
                    "is_active": True,
                    "children": [],
                    "full_path": [
                        {
                            "name": "Category 1",
                            "slug": "category-1",
                            "category_type": "Electronics",
                            "type": "Category"
                        }
                    ],
                    "images": [],
                    "sequence": 0,
                    "created_at": data["data"][1]["created_at"],
                    "updated_at": data["data"][1]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                }
            ],
            "meta": {
                "page": 1,
                "limit": 2,
                "total": 2,
                "pages": 1
            },
            "error": None
        }
        # Test second page
        response = await async_client.get(
            f"/api/v1/category-types/{category_type.id}/categories/?skip=2&limit=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [
                {
                    "id": 3,
                    "name": "Category 2",
                    "slug": "category-2",
                    "description": None,
                    "parent_id": None,
                    "category_type_id": 1,
                    "is_active": True,
                    "children": [],
                    "full_path": [
                        {
                            "name": "Category 2",
                            "slug": "category-2",
                            "category_type": "Electronics",
                            "type": "Category"
                        }
                    ],
                    "images": [],
                    "sequence": 0,
                    "created_at": data["data"][0]["created_at"],
                    "updated_at": data["data"][0]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                },
                {
                    "id": 4,
                    "name": "Category 3",
                    "slug": "category-3",
                    "description": None,
                    "parent_id": None,
                    "category_type_id": 1,
                    "is_active": True,
                    "children": [],
                    "full_path": [
                        {
                            "name": "Category 3",
                            "slug": "category-3",
                            "category_type": "Electronics",
                            "type": "Category"
                        }
                    ],
                    "images": [],
                    "sequence": 0,
                    "created_at": data["data"][1]["created_at"],
                    "updated_at": data["data"][1]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                }
            ],
            "meta": {
                "page": 2,
                "limit": 2,
                "total": 2,
                "pages": 1
            },
            "error": None
        }

    async def test_get_children_by_model_edge_cases(
        self, async_client: AsyncClient, category_type_factory, category_factory
    ):
        """Test edge cases for getting children."""
        category_type = await category_type_factory(name="Electronics")

        # Create 3 categories
        for i in range(3):
            await category_factory(
                name=f"Category {i}",
                category_type=category_type
            )

        # Test skip beyond available records
        response = await async_client.get(
            f"/api/v1/category-types/{category_type.id}/categories/?skip=10"
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [],
            "meta": {
                "page": 1,
                "limit": 100,
                "total": 0,
                "pages": 0
            },
            "error": None
        }

        # Test limit larger than available records
        response = await async_client.get(
            f"/api/v1/category-types/{category_type.id}/categories/?limit=100"
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "name": "Category 0",
                    "slug": "category-0",
                    "description": None,
                    "parent_id": None,
                    "category_type_id": 1,
                    "is_active": True,
                    "children": [],
                    "full_path": [
                        {
                            "name": "Category 0",
                            "slug": "category-0",
                            "category_type": "Electronics",
                            "type": "Category"
                        }
                    ],
                    "images": [],
                    "sequence": 0,
                    "created_at": data["data"][0]["created_at"],
                    "updated_at": data["data"][0]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                },
                {
                    "id": 2,
                    "name": "Category 1",
                    "slug": "category-1",
                    "description": None,
                    "parent_id": None,
                    "category_type_id": 1,
                    "is_active": True,
                    "children": [],
                    "full_path": [
                        {
                            "name": "Category 1",
                            "slug": "category-1",
                            "category_type": "Electronics",
                            "type": "Category"
                        }
                    ],
                    "images": [],
                    "sequence": 0,
                    "created_at": data["data"][1]["created_at"],
                    "updated_at": data["data"][1]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                },
                {
                    "id": 3,
                    "name": "Category 2",
                    "slug": "category-2",
                    "description": None,
                    "parent_id": None,
                    "category_type_id": 1,
                    "is_active": True,
                    "children": [],
                    "full_path": [
                        {
                            "name": "Category 2",
                            "slug": "category-2",
                            "category_type": "Electronics",
                            "type": "Category"
                        }
                    ],
                    "images": [],
                    "sequence": 0,
                    "created_at": data["data"][2]["created_at"],
                    "updated_at": data["data"][2]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                }
            ],
            "meta": {
                "page": 1,
                "limit": 100,
                "total": 3,
                "pages": 1
            },
            "error": None
        }

    async def test_get_children_by_model_invalid_id(self, async_client: AsyncClient):
        """Test getting children for non-existent model."""
        response = await async_client.get(
            "/api/v1/category-types/invalid/categories/"
        )
        assert response.status_code == 422
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": [
                    {
                        "loc": ["path", "category_type_id"],
                        "msg": (
                            "Input should be a valid integer, "
                            "unable to parse string as an integer"
                        ),
                        "type": "int_parsing"
                    }
                ]
            }
        }


class TestConcurrentOperations:
    """Test cases for concurrent operations."""

    async def test_concurrent_creation_same_name(self, async_client: AsyncClient):
        """Test handling concurrent creation with same name."""
        model_data = {
            "name": "Electronics"
        }

        # Create tasks for concurrent requests
        tasks = []
        for _ in range(3):
            task = async_client.post("/api/v1/category-types/", json=model_data)
            tasks.append(task)

        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Only one should succeed due to unique constraint
        success_count = 0
        error_count = 0

        for response in responses:
            if hasattr(response, 'status_code'):
                if response.status_code == 201:
                    success_count += 1
                elif response.status_code == 400:  # Duplicate name error
                    error_count += 1

        # Expect exactly one success and rest failures
        assert success_count == 1
        assert error_count == 2
