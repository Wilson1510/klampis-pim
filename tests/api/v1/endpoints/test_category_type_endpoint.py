from httpx import AsyncClient


class TestGetCategoryTypes:
    """Test cases for GET /category-types/ endpoint."""

    async def test_get_category_types_success(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test getting category types successfully."""
        # Create test data
        await category_type_factory(name="Electronics")
        await category_type_factory(name="Food")

        response = await async_client.get("/api/v1/category-types/")

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
        names = {item["name"] for item in data}
        expected_names = {"Electronics", "Food"}
        assert names == expected_names

        for item in data:
            assert "name" in item
            assert "slug" in item

    async def test_get_category_types_filter_by_name(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test filtering by name."""
        await category_type_factory(name="Electronics and Appliances")
        await category_type_factory(name="Food and Beverages")

        response = await async_client.get("/api/v1/category-types/?name=Electronics")
        assert response.status_code == 200
        data = response.json()["data"]
        print(data)
        assert len(data) == 1
        assert data[0]["name"] == "Electronics and Appliances"

    async def test_get_category_types_filter_by_slug(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test filtering by slug."""
        category_type = await category_type_factory(name="Electronics")
        await category_type_factory(name="Food")

        response = await async_client.get(
            f"/api/v1/category-types/?slug={category_type.slug}"
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["slug"] == category_type.slug

    async def test_get_category_types_filter_by_is_active(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test filtering by is_active status."""
        await category_type_factory(name="Active Type", is_active=True)
        await category_type_factory(name="Inactive Type", is_active=False)

        # Test active filter
        response = await async_client.get("/api/v1/category-types/?is_active=true")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is True

        # Test inactive filter
        response = await async_client.get("/api/v1/category-types/?is_active=false")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is False

    async def test_get_category_types_combined_filters(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test combining multiple filters."""
        category_type = await category_type_factory(
            name="Electronics", is_active=True
        )
        await category_type_factory(name="Food", is_active=False)

        response = await async_client.get(
            f"/api/v1/category-types/?slug={category_type.slug}&is_active=true"
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["slug"] == category_type.slug
        assert data[0]["is_active"] is True


class TestCreateCategoryType:
    """Test cases for POST /category-types/ endpoint."""

    async def test_create_category_type_success(self, async_client: AsyncClient):
        """Test creating category type successfully."""
        category_type_data = {"name": "Electronics"}

        response = await async_client.post(
            "/api/v1/category-types/", json=category_type_data
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Electronics"
        assert data["slug"] == "electronics"

    async def test_create_category_type_duplicate_name(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test creating category type with duplicate name."""
        await category_type_factory(name="Electronics")

        category_type_data = {"name": "Electronics"}
        response = await async_client.post(
            "/api/v1/category-types/", json=category_type_data
        )
        error = response.json()["error"]

        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Category type with name 'Electronics' already exists"
        )
        assert error["details"] is None


class TestGetCategoryType:
    """Test cases for GET /category-types/{id} endpoint."""

    async def test_get_category_type_success(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test getting category type by ID successfully."""
        category_type = await category_type_factory(name="Electronics")

        response = await async_client.get(f"/api/v1/category-types/{category_type.id}")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == category_type.id
        assert data["name"] == "Electronics"
        assert data["slug"] == category_type.slug

    async def test_get_category_type_not_found(self, async_client: AsyncClient):
        """Test getting non-existent category type."""
        response = await async_client.get("/api/v1/category-types/999")
        error = response.json()["error"]

        assert response.status_code == 404
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Category type with id 999 not found"
        assert error["details"] is None


class TestUpdateCategoryType:
    """Test cases for PUT /category-types/{id} endpoint."""

    async def test_update_category_type_success(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test updating category type successfully."""
        category_type = await category_type_factory(name="Electronics")
        assert category_type.name == "Electronics"
        assert category_type.slug == "electronics"

        update_data = {"name": "Consumer Electronics"}
        response = await async_client.put(
            f"/api/v1/category-types/{category_type.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == category_type.id
        assert data["name"] == "Consumer Electronics"
        assert data["slug"] == "consumer-electronics"

    async def test_update_category_type_not_found(self, async_client: AsyncClient):
        """Test updating non-existent category type."""
        update_data = {"name": "Updated Name"}
        response = await async_client.put(
            "/api/v1/category-types/999", json=update_data
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Category type with id 999 not found"
        assert error["details"] is None

    async def test_update_category_type_duplicate_name(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test updating category type with duplicate name."""
        await category_type_factory(name="Electronics")
        category_type2 = await category_type_factory(name="Food")

        update_data = {"name": "Electronics"}
        response = await async_client.put(
            f"/api/v1/category-types/{category_type2.id}", json=update_data
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Category type with name 'Electronics' already exists"
        )
        assert error["details"] is None


class TestDeleteCategoryType:
    """Test cases for DELETE /category-types/{id} endpoint."""

    async def test_delete_category_type_success(
        self, async_client: AsyncClient, category_type_factory
    ):
        """Test deleting category type successfully."""
        category_type = await category_type_factory(name="Electronics")

        response = await async_client.delete(
            f"/api/v1/category-types/{category_type.id}"
        )

        assert response.status_code == 204

    async def test_delete_category_type_not_found(self, async_client: AsyncClient):
        """Test deleting non-existent category type."""
        response = await async_client.delete("/api/v1/category-types/999")

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Category type with id 999 not found"
        assert error["details"] is None

    async def test_delete_category_type_with_categories(
        self, async_client: AsyncClient, category_type_factory, category_factory
    ):
        """Test deleting category type that has associated categories."""
        category_type = await category_type_factory(name="Electronics")

        # Create a category under this category type
        await category_factory(
            name="Mobile Phones",
            category_type=category_type
        )

        response = await async_client.delete(
            f"/api/v1/category-types/{category_type.id}"
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Cannot delete category type. "
            "It has 1 associated categories"
        )
        assert error["details"] is None


class TestGetCategoriesByType:
    """Test cases for GET /category-types/{id}/categories/ endpoint."""

    async def test_get_categories_by_type_success(
        self, async_client: AsyncClient, category_type_factory, category_factory
    ):
        """Test getting categories by type successfully."""
        category_type = await category_type_factory(name="Electronics")
        await category_factory(
            name="Mobile Phones", category_type=category_type
        )
        await category_factory(
            name="Laptops", category_type=category_type
        )

        # Create category with different type to ensure filtering
        other_type = await category_type_factory(name="Food")
        await category_factory(name="Beverages", category_type=other_type)

        response = await async_client.get(
            f"/api/v1/category-types/{category_type.id}/categories/"
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        for item in data:
            assert "name" in item
            assert "slug" in item

        names = {item["name"] for item in data}
        expected_names = {"Mobile Phones", "Laptops"}
        assert names == expected_names

        for item in data:
            assert "name" in item
            assert "slug" in item
            assert "description" in item
            assert "category_type_id" in item
            assert "parent_id" in item
            assert "full_path" in item
            assert "children" in item

    async def test_get_categories_by_type_not_found(self, async_client: AsyncClient):
        """Test getting categories for non-existent category type."""
        response = await async_client.get("/api/v1/category-types/999/categories/")

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Category type with id 999 not found"
        assert error["details"] is None


class TestCategoryTypeEndpointIntegration:
    """Integration tests for category type endpoints."""

    async def test_full_crud_workflow(
        self, async_client: AsyncClient
    ):
        """Test complete CRUD workflow for category types."""
        # Create
        create_data = {"name": "Electronics", "sequence": 10}
        response = await async_client.post("/api/v1/category-types/", json=create_data)
        assert response.status_code == 201
        created_data = response.json()["data"]
        category_type_id = created_data["id"]

        # Read individual
        response = await async_client.get(f"/api/v1/category-types/{category_type_id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Electronics"
        assert data["slug"] == "electronics"
        assert data["sequence"] == 10

        # Read list
        response = await async_client.get("/api/v1/category-types/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "Electronics"
        assert data[0]["slug"] == "electronics"
        assert data[0]["sequence"] == 10

        # Update
        update_data = {"name": "Consumer Electronics", "is_active": False}
        response = await async_client.put(
            f"/api/v1/category-types/{category_type_id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Consumer Electronics"
        assert data["slug"] == "consumer-electronics"
        assert data['is_active'] is False

        # Delete
        response = await async_client.delete(
            f"/api/v1/category-types/{category_type_id}"
        )
        assert response.status_code == 204

        # Verify item is deleted
        response = await async_client.get(f"/api/v1/category-types/{category_type_id}")
        assert response.status_code == 404
        error = response.json()["error"]
        assert error["message"] == f"Category type with id {category_type_id} not found"

    async def test_category_type_with_categories_workflow(
        self, async_client: AsyncClient, category_factory
    ):
        """Test category type workflow with associated categories."""
        # Create category type
        create_data = {"name": "Electronics"}
        response = await async_client.post("/api/v1/category-types/", json=create_data)
        assert response.status_code == 201
        category_type_id = response.json()["data"]["id"]

        # Create categories using factory (simulating external creation)
        await category_factory(
            name="Mobile Phones", category_type_id=category_type_id
        )
        await category_factory(
            name="Laptops", category_type_id=category_type_id
        )

        # Get categories by type
        response = await async_client.get(
            f"/api/v1/category-types/{category_type_id}/categories/"
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        assert data[0]["name"] == "Mobile Phones"
        assert data[1]["name"] == "Laptops"

        # Try to delete category type (should fail)
        response = await async_client.delete(
            f"/api/v1/category-types/{category_type_id}"
        )
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["message"] == (
            "Cannot delete category type. "
            "It has 2 associated categories"
        )
