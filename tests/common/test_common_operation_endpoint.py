"""
Common endpoint operation tests using CategoryType as example.

This module provides comprehensive tests for common CRUD operations
that can be applied to any endpoint following the same patterns.
"""

import asyncio
from httpx import AsyncClient


class TestGetAllModel:
    """Test cases for GET / endpoint with empty data."""

    async def test_get_simple_model_empty_list(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test getting models when none exist."""
        response = await async_client.get(
            "/api/v1/category-types/", headers=auth_headers_system
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

    async def test_get_simple_model_with_pagination(
        self, async_client: AsyncClient, category_type_factory, auth_headers_system
    ):
        """Test getting models with pagination."""
        # Create 5 category types
        for i in range(5):
            await category_type_factory(name=f"Category Type {i}")

        # Test first page with limit 2
        response = await async_client.get(
            "/api/v1/category-types/?skip=0&limit=2", headers=auth_headers_system
        )
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
        response = await async_client.get(
            "/api/v1/category-types/?skip=2&limit=2", headers=auth_headers_system
        )
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
        response = await async_client.get(
            "/api/v1/category-types/?skip=4&limit=2", headers=auth_headers_system
        )
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
        self, async_client: AsyncClient, category_type_factory, auth_headers_system
    ):
        """Test pagination edge cases."""
        # Create 3 category types
        for i in range(3):
            await category_type_factory(name=f"Category Type {i}")

        # Test skip beyond available records
        response = await async_client.get(
            "/api/v1/category-types/?skip=10", headers=auth_headers_system
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
            "/api/v1/category-types/?limit=100", headers=auth_headers_system
        )
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
        response = await async_client.get(
            "/api/v1/category-types/?skip=-1", headers=auth_headers_system
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
                        "loc": ["query", "skip"],
                        "msg": "Input should be greater than or equal to 0",
                        "type": "greater_than_equal"
                    }
                ]
            }
        }

        response = await async_client.get(
            "/api/v1/category-types/?limit=0", headers=auth_headers_system
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
                        "loc": ["query", "limit"],
                        "msg": "Input should be greater than or equal to 1",
                        "type": "greater_than_equal"
                    }
                ]
            }
        }

        response = await async_client.get(
            "/api/v1/category-types/?limit=1001", headers=auth_headers_system
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
                        "loc": ["query", "limit"],
                        "msg": "Input should be less than or equal to 1000",
                        "type": "less_than_equal"
                    }
                ]
            }
        }

    async def test_get_simple_model_with_images(
        self, async_client: AsyncClient, category_factory, image_factory,
        auth_headers_system
    ):
        """Test getting model with image."""
        category = await category_factory(name="Electronics")
        await category_factory(name="Mobile Phones")
        await image_factory(
            file="test_folder/test1.jpg",
            object_id=category.id,
            content_type="categories"
        )
        await image_factory(
            file="test_folder/test2.jpg",
            object_id=category.id,
            content_type="categories"
        )
        response = await async_client.get(
            "/api/v1/categories/", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "name": "Electronics",
                    "slug": "electronics",
                    "sequence": 0,
                    "description": None,
                    "parent_id": None,
                    "category_type_id": 1,
                    "is_active": True,
                    "children": [],
                    "full_path": [
                        {
                            "name": "Electronics",
                            "slug": "electronics",
                            "category_type": "Test Category Type",
                            "type": "Category"
                        }
                    ],
                    "images": [
                        {
                            "id": 1,
                            "file": "test_folder/test1.jpg",
                            "title": None,
                            "is_primary": False
                        },
                        {
                            "id": 2,
                            "file": "test_folder/test2.jpg",
                            "title": None,
                            "is_primary": False
                        }
                    ],
                    "created_at": data["data"][0]["created_at"],
                    "updated_at": data["data"][0]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                },
                {
                    "id": 2,
                    "name": "Mobile Phones",
                    "slug": "mobile-phones",
                    "sequence": 0,
                    "description": None,
                    "parent_id": None,
                    "category_type_id": 1,
                    "is_active": True,
                    "children": [],
                    "full_path": [
                        {
                            "name": "Mobile Phones",
                            "slug": "mobile-phones",
                            "category_type": "Test Category Type",
                            "type": "Category"
                        }
                    ],
                    "images": [],
                    "created_at": data["data"][1]["created_at"],
                    "updated_at": data["data"][1]["updated_at"],
                    "created_by": 1,
                    "updated_by": 1
                }
            ],
            "meta": {
                "page": 1,
                "limit": 100,
                "total": 2,
                "pages": 1
            },
            "error": None
        }


class TestCreateModel:
    """Test cases for POST / endpoint."""

    async def test_create_simple_model_with_all_fields_provided(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating model with all fields provided."""
        model_data = {
            "name": "Electronics and Gadgets",
            "is_active": True,
            "sequence": 10
        }

        response = await async_client.post(
            "/api/v1/category-types/",
            json=model_data,
            headers=auth_headers_system
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
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating model with only required fields."""
        model_data = {
            "name": "Food and Beverages"
        }

        response = await async_client.post(
            "/api/v1/category-types/",
            json=model_data,
            headers=auth_headers_system
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
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating model with missing required fields."""
        model_data = {
            "company_type": "PT",
            "name": "PT Maju Jaya"
        }

        response = await async_client.post(
            "/api/v1/suppliers/",
            json=model_data,
            headers=auth_headers_system
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
                        "loc": ["body", "contact"],
                        "msg": "Field required",
                        "type": "missing"
                    },
                    {
                        "loc": ["body", "email"],
                        "msg": "Field required",
                        "type": "missing"
                    }
                ]
            }
        }

    async def test_create_simple_model_with_only_optional_fields(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating model with only optional fields (should fail)."""
        model_data = {
            "is_active": False,
            "sequence": 10,
            "address": "Jl. Sudirman No. 123",
        }

        response = await async_client.post(
            "/api/v1/suppliers/",
            json=model_data,
            headers=auth_headers_system
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
                    },
                    {
                        "loc": ["body", "company_type"],
                        "msg": "Field required",
                        "type": "missing"
                    },
                    {
                        "loc": ["body", "contact"],
                        "msg": "Field required",
                        "type": "missing"
                    },
                    {
                        "loc": ["body", "email"],
                        "msg": "Field required",
                        "type": "missing"
                    }
                ]
            }
        }

    async def test_create_simple_model_with_no_fields(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating model with no fields provided."""
        response = await async_client.post(
            "/api/v1/category-types/",
            json={},
            headers=auth_headers_system
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

    async def test_create_simple_model_invalid_parent_id(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating model with invalid parent id."""
        category_data = {
            "name": "Mobile Phones",
            "category_type_id": 999
        }
        response = await async_client.post(
            "/api/v1/categories/",
            json=category_data,
            headers=auth_headers_system
        )
        assert response.status_code == 404
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "HTTP_ERROR_404",
                "message": "CategoryTypes with id 999 not found",
                "details": None
            }
        }

    async def test_create_simple_model_with_images(
        self, async_client: AsyncClient, category_type_factory, auth_headers_system
    ):
        """Test creating model with images."""
        category_type = await category_type_factory(name="Electronics")
        category_data = {
            "name": "Mobile Phones",
            "category_type_id": category_type.id,
            "images": [
                {
                    "file": "test_folder/test1.jpg",
                    "title": "Test Image 1",
                    "is_primary": True
                },
                {
                    "file": "test_folder/test2.jpg",
                    "title": "Test Image 2",
                    "is_primary": False
                }
            ]
        }

        response = await async_client.post(
            "/api/v1/categories/",
            json=category_data,
            headers=auth_headers_system
        )
        assert response.status_code == 201
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Mobile Phones",
                "slug": "mobile-phones",
                "sequence": 0,
                "description": None,
                "parent_id": None,
                "category_type_id": 1,
                "is_active": True,
                "children": [],
                "full_path": [
                    {
                        "name": "Mobile Phones",
                        "slug": "mobile-phones",
                        "category_type": "Electronics",
                        "type": "Category"
                    }
                ],
                "images": [
                    {
                        "id": 1,
                        "file": "test_folder/test1.jpg",
                        "title": "Test Image 1",
                        "is_primary": True
                    },
                    {
                        "id": 2,
                        "file": "test_folder/test2.jpg",
                        "title": "Test Image 2",
                        "is_primary": False
                    }
                ],
                "sequence": 0,
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None,
        }


class TestGetModel:
    """Test cases for GET /{id} endpoint."""

    async def test_get_simple_model_with_images(
        self, async_client: AsyncClient, category_factory, image_factory,
        auth_headers_system
    ):
        """Test getting model with image."""
        category = await category_factory(name="Electronics")
        await image_factory(
            file="test_folder/test1.jpg",
            object_id=category.id,
            content_type="categories"
        )
        await image_factory(
            file="test_folder/test2.jpg",
            object_id=category.id,
            content_type="categories"
        )
        response = await async_client.get(
            f"/api/v1/categories/{category.id}",
            headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Electronics",
                "slug": "electronics",
                "sequence": 0,
                "description": None,
                "parent_id": None,
                "category_type_id": 1,
                "is_active": True,
                "children": [],
                "full_path": [
                    {
                        "name": "Electronics",
                        "slug": "electronics",
                        "category_type": "Test Category Type",
                        "type": "Category"
                    }
                ],
                "images": [
                    {
                        "id": 1,
                        "file": "test_folder/test1.jpg",
                        "title": None,
                        "is_primary": False
                    },
                    {
                        "id": 2,
                        "file": "test_folder/test2.jpg",
                        "title": None,
                        "is_primary": False
                    }
                ],
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None
        }


class TestUpdateModel:
    """Test cases for PUT /{id} endpoint."""

    async def test_update_simple_model_with_all_fields_provided(
        self, async_client: AsyncClient, category_type_factory, auth_headers_system
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
            json=update_data,
            headers=auth_headers_system
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
        self, async_client: AsyncClient, category_type_factory, auth_headers_system
    ):
        """Test updating model with empty request body."""
        category_type = await category_type_factory(
            name="Original Name",
            sequence=10
        )

        response = await async_client.put(
            f"/api/v1/category-types/{category_type.id}",
            json={},
            headers=auth_headers_system
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
        self, async_client: AsyncClient, category_type_factory, auth_headers_system
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
            json=update_data,
            headers=auth_headers_system
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

    async def test_update_simple_model_change_parent_id(
        self, async_client: AsyncClient, category_factory, product_factory,
        auth_headers_system
    ):
        """Test updating model with new parent id."""
        category = await category_factory(name="Electronics")
        category2 = await category_factory(name="Mobile Phones")
        product = await product_factory(name="iPhone 15", category_id=category.id)
        update_data = {
            "category_id": category2.id
        }
        response = await async_client.put(
            f"/api/v1/products/{product.id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "iPhone 15",
                "slug": "iphone-15",
                "category_id": category2.id,
                "supplier_id": 1,
                "sequence": 0,
                "description": None,
                "is_active": True,
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1,
                "images": [],
                "full_path": [
                    {
                        "name": "Mobile Phones",
                        "slug": "mobile-phones",
                        "category_type": "Test Category Type",
                        "type": "Category"
                    },
                    {
                        "name": "iPhone 15",
                        "slug": "iphone-15",
                        "type": "Product"
                    }
                ]
            },
            "error": None
        }

    async def test_update_simple_model_invalid_parent_id(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test updating model with invalid parent id."""
        category = await category_factory(name="Electronics")
        update_data = {
            "category_type_id": 999
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 404
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "HTTP_ERROR_404",
                "message": "CategoryTypes with id 999 not found",
                "details": None
            }
        }

    async def test_update_simple_model_with_all_images_fields_provided(
        self, async_client: AsyncClient, category_factory, image_factory,
        auth_headers_system
    ):
        """Test updating model with images."""
        category = await category_factory(name="Electronics")
        image = await image_factory(
            file="test_folder/test1.jpg",
            object_id=category.id,
            content_type="categories"
        )
        image2 = await image_factory(
            file="test_folder/test2.jpg",
            object_id=category.id,
            content_type="categories"
        )
        update_data = {
            "name": "Updated Electronics",
            "images_to_create": [
                {
                    "file": "test_folder/test3.jpg",
                    "title": "Test Image 3",
                    "is_primary": True
                }
            ],
            "images_to_update": [
                {
                    "id": image2.id,
                    "file": "test_folder/test8.jpg",
                    "title": "Test Image 2",
                    "is_primary": False
                }
            ],
            "images_to_delete": [
                image.id
            ]
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Updated Electronics",
                "slug": "updated-electronics",
                "sequence": 0,
                "description": None,
                "parent_id": None,
                "category_type_id": 1,
                "is_active": True,
                "children": [],
                "full_path": [
                    {
                        "name": "Updated Electronics",
                        "slug": "updated-electronics",
                        "category_type": "Test Category Type",
                        "type": "Category"
                    }
                ],
                "images": [
                    {
                        "id": 3,
                        "file": "test_folder/test3.jpg",
                        "title": "Test Image 3",
                        "is_primary": True
                    },
                    {
                        "id": 2,
                        "file": "test_folder/test8.jpg",
                        "title": "Test Image 2",
                        "is_primary": False
                    }
                ],
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None
        }

    async def test_update_simple_model_with_images_to_create_only(
        self, async_client: AsyncClient, category_factory, image_factory,
        auth_headers_system
    ):
        """Test updating model with images."""
        category = await category_factory(name="Electronics")
        await image_factory(
            file="test_folder/test1.jpg",
            object_id=category.id,
            content_type="categories"
        )
        update_data = {
            "name": "Updated Electronics",
            "images_to_create": [
                {
                    "file": "test_folder/test3.jpg",
                    "title": "Test Image 3",
                    "is_primary": True
                }
            ]
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Updated Electronics",
                "slug": "updated-electronics",
                "sequence": 0,
                "description": None,
                "parent_id": None,
                "category_type_id": 1,
                "is_active": True,
                "children": [],
                "full_path": [
                    {
                        "name": "Updated Electronics",
                        "slug": "updated-electronics",
                        "category_type": "Test Category Type",
                        "type": "Category"
                    }
                ],
                "images": [
                    {
                        "id": 1,
                        "file": "test_folder/test1.jpg",
                        "title": None,
                        "is_primary": False
                    },
                    {
                        "id": 2,
                        "file": "test_folder/test3.jpg",
                        "title": "Test Image 3",
                        "is_primary": True
                    }
                ],
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None
        }

    async def test_update_simple_model_with_images_to_update_only(
        self, async_client: AsyncClient, category_factory, image_factory,
        auth_headers_system
    ):
        """Test updating model with images."""
        category = await category_factory(name="Electronics")
        await image_factory(
            file="test_folder/test1.jpg",
            object_id=category.id,
            content_type="categories"
        )
        image2 = await image_factory(
            file="test_folder/test2.jpg",
            object_id=category.id,
            content_type="categories"
        )
        update_data = {
            "name": "Updated Electronics",
            "images_to_update": [
                {
                    "id": image2.id,
                    "file": "test_folder/test8.jpg",
                    "title": "Test Image 2",
                    "is_primary": True
                }
            ],
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Updated Electronics",
                "slug": "updated-electronics",
                "sequence": 0,
                "description": None,
                "parent_id": None,
                "category_type_id": 1,
                "is_active": True,
                "children": [],
                "full_path": [
                    {
                        "name": "Updated Electronics",
                        "slug": "updated-electronics",
                        "category_type": "Test Category Type",
                        "type": "Category"
                    }
                ],
                "images": [
                    {
                        "id": 1,
                        "file": "test_folder/test1.jpg",
                        "title": None,
                        "is_primary": False
                    },
                    {
                        "id": 2,
                        "file": "test_folder/test8.jpg",
                        "title": "Test Image 2",
                        "is_primary": True
                    }
                ],
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None
        }

    async def test_update_simple_model_with_images_to_delete_only(
        self, async_client: AsyncClient, category_factory, image_factory,
        auth_headers_system
    ):
        """Test updating model with images."""
        category = await category_factory(name="Electronics")
        await image_factory(
            file="test_folder/test1.jpg",
            object_id=category.id,
            content_type="categories"
        )
        image2 = await image_factory(
            file="test_folder/test2.jpg",
            object_id=category.id,
            content_type="categories"
        )
        update_data = {
            "name": "Updated Electronics",
            "images_to_delete": [
                image2.id
            ]
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "success": True,
            "data": {
                "id": 1,
                "name": "Updated Electronics",
                "slug": "updated-electronics",
                "sequence": 0,
                "description": None,
                "parent_id": None,
                "category_type_id": 1,
                "is_active": True,
                "children": [],
                "full_path": [
                    {
                        "name": "Updated Electronics",
                        "slug": "updated-electronics",
                        "category_type": "Test Category Type",
                        "type": "Category"
                    }
                ],
                "images": [
                    {
                        "id": 1,
                        "file": "test_folder/test1.jpg",
                        "title": None,
                        "is_primary": False
                    }
                ],
                "created_at": data["data"]["created_at"],
                "updated_at": data["data"]["updated_at"],
                "created_by": 1,
                "updated_by": 1
            },
            "error": None
        }

    async def test_update_simple_model_invalid_image_id(
        self, async_client: AsyncClient, category_factory, image_factory,
        auth_headers_system
    ):
        """Test updating model with invalid image id."""
        category = await category_factory(name="Electronics")
        await image_factory(
            file="test_folder/test1.jpg",
            object_id=category.id,
            content_type="categories"
        )
        update_data = {
            "images_to_update": [
                {
                    "id": 999,
                    "file": "test_folder/test8.jpg"
                }
            ]
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 404
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "HTTP_ERROR_404",
                "message": "Image with id 999 not found",
                "details": None
            }
        }

        update_data = {
            "images_to_delete": [999, 1000]
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 404
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "HTTP_ERROR_404",
                "message": "Image with id 999 not found",
                "details": None
            }
        }

    async def test_update_simple_model_image_object_id_mismatch(
        self, async_client: AsyncClient, category_factory, image_factory,
        auth_headers_system
    ):
        """Test updating model with object id mismatch."""
        category = await category_factory(name="Electronics")
        await image_factory(
            file="test_folder/test1.jpg",
            object_id=category.id,
            content_type="categories"
        )
        category2 = await category_factory(name="Food")
        await image_factory(
            file="test_folder/test2.jpg",
            object_id=category2.id,
            content_type="categories"
        )
        update_data = {
            "images_to_update": [
                {
                    "id": 2,
                    "file": "test_folder/test8.jpg",
                    "title": "Test Image 2",
                    "is_primary": True
                }
            ]
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 400
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "HTTP_ERROR_400",
                "message": "Image with id 2 does not belong to Categories with id 1",
                "details": None
            }
        }

        update_data = {
            "images_to_delete": [2]
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 400
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "HTTP_ERROR_400",
                "message": "Image with id 2 does not belong to Categories with id 1",
                "details": None
            }
        }

    async def test_update_simple_model_invalid_image_content_type(
        self, async_client: AsyncClient, category_factory, image_factory,
        auth_headers_system
    ):
        """Test updating model with invalid image content type."""
        category = await category_factory(name="Electronics")
        await image_factory(
            file="test_folder/test1.jpg",
            object_id=category.id,
            content_type="categories"
        )
        await image_factory(
            file="test_folder/test2.jpg",
            object_id=category.id,
            content_type="products"
        )
        update_data = {
            "images_to_update": [
                {
                    "id": 2,
                    "file": "test_folder/test8.jpg",
                    "title": "Test Image 2",
                    "is_primary": True
                }
            ]
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 400
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "HTTP_ERROR_400",
                "message": "Image with id 2 is not a categories image",
                "details": None
            }
        }

        update_data = {
            "images_to_delete": [2]
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 400
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "HTTP_ERROR_400",
                "message": "Image with id 2 is not a categories image",
                "details": None
            }
        }


class TestGetChildrenByModel:
    """Test cases for GET /{id}/children endpoint."""

    async def test_get_children_by_model_empty_list(
        self, async_client: AsyncClient, category_type_factory, auth_headers_system
    ):
        """Test getting children when none exist."""
        category_type = await category_type_factory(name="Electronics")

        response = await async_client.get(
            f"/api/v1/category-types/{category_type.id}/categories/",
            headers=auth_headers_system
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
        self, async_client: AsyncClient, category_type_factory, category_factory,
        auth_headers_system
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
            f"/api/v1/category-types/{category_type.id}/categories/?skip=0&limit=2",
            headers=auth_headers_system
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
            f"/api/v1/category-types/{category_type.id}/categories/?skip=2&limit=2",
            headers=auth_headers_system
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
        self, async_client: AsyncClient, category_type_factory, category_factory,
        auth_headers_system
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
            f"/api/v1/category-types/{category_type.id}/categories/?skip=10",
            headers=auth_headers_system
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
            f"/api/v1/category-types/{category_type.id}/categories/?limit=100",
            headers=auth_headers_system
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

    async def test_get_children_by_model_invalid_id(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test getting children for non-existent model."""
        response = await async_client.get(
            "/api/v1/category-types/invalid/categories/",
            headers=auth_headers_system
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

    async def test_concurrent_creation_same_name(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test handling concurrent creation with same name."""
        model_data = {
            "name": "Electronics"
        }

        # Create tasks for concurrent requests
        tasks = []
        for _ in range(3):
            task = async_client.post(
                "/api/v1/category-types/",
                json=model_data,
                headers=auth_headers_system
            )
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
