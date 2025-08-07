from httpx import AsyncClient


class TestGetCategories:
    """Test cases for GET /categories/ endpoint."""

    async def test_get_categories_success(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test getting categories successfully."""
        # Create test data
        await category_factory(name="Mobile Phones")
        await category_factory(name="Laptops")

        response = await async_client.get(
            "/api/v1/categories/", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
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
            assert "images" in item

    async def test_get_categories_filter_by_name(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test filtering by name."""
        await category_factory(name="Mobile Phones and Accessories")
        await category_factory(name="Laptops and Computers")

        response = await async_client.get(
            "/api/v1/categories/?name=Mobile", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "Mobile Phones and Accessories"

    async def test_get_categories_filter_by_slug(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test filtering by slug."""
        await category_factory(name="Mobile Phones")
        await category_factory(name="Laptops")

        response = await async_client.get(
            "/api/v1/categories/?slug=mobile-phones", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["slug"] == "mobile-phones"

    async def test_get_categories_filter_by_category_type_id(
        self, async_client: AsyncClient, category_factory, category_type_factory,
        auth_headers_system
    ):
        """Test filtering by category_type_id."""
        electronics_type = await category_type_factory(name="Electronics")
        food_type = await category_type_factory(name="Food")

        await category_factory(
            name="Mobile Phones",
            category_type=electronics_type
        )
        await category_factory(
            name="Beverages",
            category_type=food_type
        )

        response = await async_client.get(
            f"/api/v1/categories/?category_type_id={electronics_type.id}",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["category_type_id"] == electronics_type.id

    async def test_get_categories_filter_by_parent_id(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test filtering by parent_id."""
        parent_category = await category_factory(name="Mobile Phones")
        await category_factory(
            name="Smartphones",
            parent_id=parent_category.id
        )
        await category_factory(
            name="Feature Phones",
            parent_id=parent_category.id
        )

        response = await async_client.get(
            f"/api/v1/categories/?parent_id={parent_category.id}",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        for item in data:
            assert item["parent_id"] == parent_category.id

    async def test_get_categories_filter_by_is_active(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test filtering by is_active status."""
        await category_factory(name="Active Category", is_active=True)
        await category_factory(name="Inactive Category", is_active=False)

        # Test active filter
        response = await async_client.get(
            "/api/v1/categories/?is_active=true", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is True

        # Test inactive filter
        response = await async_client.get(
            "/api/v1/categories/?is_active=false", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is False

    async def test_get_categories_combined_filters(
        self, async_client: AsyncClient, category_factory, category_type_factory,
        auth_headers_system
    ):
        """Test combining multiple filters."""
        electronics_type = await category_type_factory(name="Electronics")
        food_type = await category_type_factory(name="Food")

        await category_factory(
            name="Mobile Phones",
            category_type=electronics_type,
            is_active=True
        )
        await category_factory(
            name="Beverages",
            category_type=food_type,
            is_active=False
        )

        response = await async_client.get(
            f"/api/v1/categories/?category_type_id={electronics_type.id}&is_act"
            "ive=true",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["category_type_id"] == electronics_type.id
        assert data[0]["is_active"] is True

    async def test_get_categories_by_user(
        self, async_client: AsyncClient, category_factory, auth_headers_user
    ):
        """Test getting categories by user."""
        await category_factory(name="Mobile Phones")
        await category_factory(name="Laptops")

        response = await async_client.get(
            "/api/v1/categories/", headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
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

    async def test_get_categories_unauthenticated(
        self, async_client: AsyncClient
    ):
        """Test getting categories without authentication."""
        response = await async_client.get("/api/v1/categories/")
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestCreateCategory:
    """Test cases for POST /categories/ endpoint."""

    async def test_create_top_level_category_success(
        self, async_client: AsyncClient, category_type_factory, auth_headers_system
    ):
        """Test creating top-level category successfully."""
        category_type = await category_type_factory(name="Electronics")

        category_data = {
            "name": "Mobile Phones",
            "description": "Mobile phones and accessories",
            "category_type_id": category_type.id
        }

        response = await async_client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers_system
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Mobile Phones"
        assert data["slug"] == "mobile-phones"
        assert data["category_type_id"] == category_type.id
        assert data["parent_id"] is None
        assert len(data['full_path']) == 1

    async def test_create_child_category_success(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test creating child category successfully."""
        parent_category = await category_factory(name="Mobile Phones")

        category_data = {
            "name": "Smartphones",
            "description": "Smart mobile phones",
            "parent_id": parent_category.id
        }

        response = await async_client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers_system
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Smartphones"
        assert data["slug"] == "smartphones"
        assert data["parent_id"] == parent_category.id
        assert data["category_type_id"] is None
        assert len(data['full_path']) == 2

    async def test_create_category_duplicate_name(
        self, async_client: AsyncClient, category_factory, category_type_factory,
        auth_headers_system
    ):
        """Test creating category with duplicate name."""
        category_type = await category_type_factory(name="Electronics")
        await category_factory(
            name="Mobile Phones",
            category_type=category_type
        )

        category_data = {
            "name": "Mobile Phones",
            "category_type_id": category_type.id
        }
        response = await async_client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Category with name 'Mobile Phones' already exists"
        )
        assert error["details"] is None

    async def test_create_top_level_category_without_category_type_id(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating top-level category without category_type_id (should fail)."""
        category_data = {
            "name": "Mobile Phones",
            "description": "Mobile phones and accessories"
        }

        response = await async_client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers_system
        )

        assert response.status_code == 422
        errors = response.json()["error"]
        assert errors["code"] == "VALIDATION_ERROR"
        assert errors["message"] == "Validation error"
        assert errors["details"][0]["loc"] == ["body"]
        assert errors["details"][0]["msg"] == (
            "Value error, Top-level categories must have a category_type_id"
        )
        assert errors["details"][0]["type"] == "value_error"

    async def test_create_child_category_with_category_type_id(
        self, async_client: AsyncClient, category_factory, category_type_factory,
        auth_headers_system
    ):
        """Test creating child category with category_type_id (should fail)."""
        category_type = await category_type_factory(name="Electronics")
        parent_category = await category_factory(
            name="Mobile Phones",
            category_type=category_type
        )

        category_data = {
            "name": "Smartphones",
            "parent_id": parent_category.id,
            "category_type_id": category_type.id
        }

        response = await async_client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers_system
        )

        assert response.status_code == 422
        errors = response.json()["error"]
        assert errors["code"] == "VALIDATION_ERROR"
        assert errors["message"] == "Validation error"
        assert errors["details"][0]["loc"] == ["body"]
        assert errors["details"][0]["msg"] == (
            "Value error, Child categories must not have a category_type_id"
        )
        assert errors["details"][0]["type"] == "value_error"

    async def test_create_category_by_user(
        self, async_client: AsyncClient, category_type_factory, auth_headers_user
    ):
        """Test creating category by user."""
        category_type = await category_type_factory(name="Electronics")

        category_data = {
            "name": "Mobile Phones",
            "description": "Mobile phones and accessories",
            "category_type_id": category_type.id
        }

        response = await async_client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers_user
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Mobile Phones"
        assert data["slug"] == "mobile-phones"
        assert data["category_type_id"] == category_type.id

    async def test_create_category_unauthenticated(
        self, async_client: AsyncClient
    ):
        """Test creating category without authentication."""
        category_data = {
            "name": "Mobile Phones",
            "description": "Mobile phones and accessories",
            "category_type_id": 1
        }

        response = await async_client.post(
            "/api/v1/categories/", json=category_data
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestGetCategory:
    """Test cases for GET /categories/{id} endpoint."""

    async def test_get_category_success(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test getting category by ID successfully."""
        category = await category_factory(name="Mobile Phones")

        response = await async_client.get(
            f"/api/v1/categories/{category.id}", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == category.id
        assert data["name"] == "Mobile Phones"
        assert data["slug"] == category.slug
        assert len(data['full_path']) == 1

    async def test_get_category_with_hierarchy(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test getting category with full hierarchy."""
        parent_category = await category_factory(name="Mobile Phones")
        child_category = await category_factory(
            name="Smartphones",
            parent=parent_category
        )

        response = await async_client.get(
            f"/api/v1/categories/{child_category.id}", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == child_category.id
        assert data["parent_id"] == parent_category.id
        assert len(data["full_path"]) == 2
        assert data["full_path"][0]["name"] == "Mobile Phones"
        assert data["full_path"][1]["name"] == "Smartphones"

    async def test_get_category_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test getting non-existent category."""
        response = await async_client.get(
            "/api/v1/categories/999", headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Category with id 999 not found"
        assert error["details"] is None

    async def test_get_category_by_user(
        self, async_client: AsyncClient, category_factory, auth_headers_user
    ):
        """Test getting category by ID by user."""
        category = await category_factory(name="Mobile Phones")

        response = await async_client.get(
            f"/api/v1/categories/{category.id}", headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == category.id
        assert data["name"] == "Mobile Phones"
        assert data["slug"] == category.slug

    async def test_get_category_unauthenticated(
        self, async_client: AsyncClient, category_factory
    ):
        """Test getting category by ID without authentication."""
        category = await category_factory(name="Mobile Phones")

        response = await async_client.get(
            f"/api/v1/categories/{category.id}"
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestUpdateCategory:
    """Test cases for PUT /categories/{id} endpoint."""

    async def test_update_category_success(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test updating category successfully."""
        category = await category_factory(name="Mobile Phones")

        update_data = {
            "name": "Mobile Phones and Accessories",
            "description": "Updated description"
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == category.id
        assert data["name"] == "Mobile Phones and Accessories"
        assert data["slug"] == "mobile-phones-and-accessories"
        assert data["description"] == "Updated description"

    async def test_update_category_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test updating non-existent category."""
        update_data = {"name": "Updated Name"}
        response = await async_client.put(
            "/api/v1/categories/999",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Category with id 999 not found"
        assert error["details"] is None

    async def test_update_category_duplicate_name(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test updating category with duplicate name."""
        await category_factory(name="Mobile Phones")
        category2 = await category_factory(name="Laptops")

        update_data = {"name": "Mobile Phones"}
        response = await async_client.put(
            f"/api/v1/categories/{category2.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Category with name 'Mobile Phones' already exists"
        )
        assert error["details"] is None

    async def test_update_category_parent_category_type_not_null(
        self, async_client: AsyncClient, category_factory, category_type_factory,
        auth_headers_system
    ):
        """Test updating category with parent category type not null."""
        category_type = await category_type_factory(name="Electronics")
        parent_category = await category_factory(name="Mobile Phones")
        category2 = await category_factory(name="Laptops", parent=parent_category)

        update_data = {
            "name": "Laptops updated",
            "category_type_id": category_type.id,
            "parent_id": parent_category.id
        }
        response = await async_client.put(
            f"/api/v1/categories/{category2.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Child categories must not have a category_type_id"
        )
        assert error["details"] is None

    async def test_update_category_parent_not_exists(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test updating category with parent category type not null."""
        parent_category = await category_factory(name="Mobile Phones")
        category = await category_factory(name="Laptops", parent=parent_category)

        update_data = {
            "name": "Laptops updated",
            "parent_id": 999
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == (
            "Categories with id 999 not found"
        )
        assert error["details"] is None

    async def test_update_category_parent_self(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test updating category with parent category type not null."""
        parent_category = await category_factory(name="Mobile Phones")
        category = await category_factory(name="Laptops", parent=parent_category)

        update_data = {
            "name": "Laptops updated",
            "parent_id": category.id
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "A category cannot be its own parent"
        )
        assert error["details"] is None

    async def test_update_category_category_type_not_exists(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test updating category with parent category type not null."""
        category = await category_factory(name="Mobile Phones")

        update_data = {
            "name": "Laptops updated",
            "category_type_id": 999
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}", json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == (
            "CategoryTypes with id 999 not found"
        )
        assert error["details"] is None

    async def test_update_category_by_user(
        self, async_client: AsyncClient, category_factory, auth_headers_user
    ):
        """Test updating category by user."""
        category = await category_factory(name="Mobile Phones")

        update_data = {
            "name": "Mobile Phones and Accessories",
            "description": "Updated description"
        }
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data,
            headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

    async def test_update_category_unauthenticated(
        self, async_client: AsyncClient, category_factory
    ):
        """Test updating category without authentication."""
        category = await category_factory(name="Mobile Phones")

        update_data = {"name": "Mobile Phones and Accessories"}
        response = await async_client.put(
            f"/api/v1/categories/{category.id}",
            json=update_data
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestDeleteCategory:
    """Test cases for DELETE /categories/{id} endpoint."""

    async def test_delete_category_success(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test deleting category successfully."""
        category = await category_factory(name="Mobile Phones")

        response = await async_client.delete(
            f"/api/v1/categories/{category.id}", headers=auth_headers_system
        )

        assert response.status_code == 204

    async def test_delete_category_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test deleting non-existent category."""
        response = await async_client.delete(
            "/api/v1/categories/999", headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Category with id 999 not found"
        assert error["details"] is None

    async def test_delete_category_with_children(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test deleting category that has child categories."""
        parent_category = await category_factory(name="Mobile Phones")

        # Create a child category
        await category_factory(
            name="Smartphones",
            parent=parent_category
        )

        response = await async_client.delete(
            f"/api/v1/categories/{parent_category.id}", headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Cannot delete category. It has 1 child categories"
        )
        assert error["details"] is None

    async def test_delete_category_with_products(
        self, async_client: AsyncClient, category_factory, product_factory,
        auth_headers_system
    ):
        """Test deleting category that has products."""
        category = await category_factory(name="Mobile Phones")

        # Create a product in this category
        await product_factory(name="iPhone 15", category_id=category.id)

        response = await async_client.delete(
            f"/api/v1/categories/{category.id}", headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Cannot delete category. It has 1 products"
        )
        assert error["details"] is None

    async def test_delete_category_by_user(
        self, async_client: AsyncClient, category_factory, auth_headers_user
    ):
        """Test deleting category by user."""
        category = await category_factory(name="Mobile Phones")

        response = await async_client.delete(
            f"/api/v1/categories/{category.id}", headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

    async def test_delete_category_unauthenticated(
        self, async_client: AsyncClient, category_factory
    ):
        """Test deleting category without authentication."""
        category = await category_factory(name="Mobile Phones")

        response = await async_client.delete(
            f"/api/v1/categories/{category.id}"
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestGetCategoryChildren:
    """Test cases for GET /categories/{id}/children/ endpoint."""

    async def test_get_category_children_success(
        self, async_client: AsyncClient, category_factory, auth_headers_system
    ):
        """Test getting category children successfully."""
        parent_category = await category_factory(name="Mobile Phones")
        await category_factory(name="Smartphones", parent=parent_category)
        await category_factory(name="Feature Phones", parent=parent_category)

        # Create category with different parent to ensure filtering
        other_parent = await category_factory(name="Laptops")
        await category_factory(name="Gaming Laptops", parent=other_parent)

        response = await async_client.get(
            f"/api/v1/categories/{parent_category.id}/children/",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        names = {item["name"] for item in data}
        expected_names = {"Smartphones", "Feature Phones"}
        assert names == expected_names

        for item in data:
            assert item["parent_id"] == parent_category.id
            assert "name" in item
            assert "slug" in item
            assert "description" in item
            assert "full_path" in item
            assert "children" in item
            assert "images" in item

    async def test_get_category_children_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test getting children for non-existent category."""
        response = await async_client.get(
            "/api/v1/categories/999/children/", headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Parent category with id 999 not found"
        assert error["details"] is None

    async def test_get_category_children_by_user(
        self, async_client: AsyncClient, category_factory, auth_headers_user
    ):
        """Test getting category children by user."""
        parent_category = await category_factory(name="Mobile Phones")
        await category_factory(name="Smartphones", parent=parent_category)
        await category_factory(name="Feature Phones", parent=parent_category)

        response = await async_client.get(
            f"/api/v1/categories/{parent_category.id}/children/",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        names = {item["name"] for item in data}
        expected_names = {"Smartphones", "Feature Phones"}
        assert names == expected_names

        for item in data:
            assert item["parent_id"] == parent_category.id

    async def test_get_category_children_unauthenticated(
        self, async_client: AsyncClient, category_factory
    ):
        """Test getting category children without authentication."""
        parent_category = await category_factory(name="Mobile Phones")

        response = await async_client.get(
            f"/api/v1/categories/{parent_category.id}/children/"
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestGetCategoryProducts:
    """Test cases for GET /categories/{id}/products/ endpoint."""

    async def test_get_category_products_success(
        self, async_client: AsyncClient, category_factory, product_factory,
        auth_headers_system
    ):
        """Test getting category products successfully."""
        category = await category_factory(name="Mobile Phones")
        await product_factory(name="iPhone 15", category_id=category.id)
        await product_factory(name="Samsung Galaxy S24", category_id=category.id)

        # Create product in different category to ensure filtering
        other_category = await category_factory(name="Laptops")
        await product_factory(name="MacBook Pro", category_id=other_category.id)

        response = await async_client.get(
            f"/api/v1/categories/{category.id}/products/",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        names = {item["name"] for item in data}
        expected_names = {"iPhone 15", "Samsung Galaxy S24"}
        assert names == expected_names

        for item in data:
            assert item["category_id"] == category.id
            assert "name" in item
            assert "slug" in item
            assert "description" in item
            assert "full_path" in item
            assert "images" in item

    async def test_get_category_products_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test getting products for non-existent category."""
        response = await async_client.get(
            "/api/v1/categories/999/products/", headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Category with id 999 not found"
        assert error["details"] is None

    async def test_get_category_products_by_user(
        self, async_client: AsyncClient, category_factory, product_factory,
        auth_headers_user
    ):
        """Test getting category products by user."""
        category = await category_factory(name="Mobile Phones")
        await product_factory(name="iPhone 15", category_id=category.id)
        await product_factory(name="Samsung Galaxy S24", category_id=category.id)

        response = await async_client.get(
            f"/api/v1/categories/{category.id}/products/",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        names = {item["name"] for item in data}
        expected_names = {"iPhone 15", "Samsung Galaxy S24"}
        assert names == expected_names

        for item in data:
            assert item["category_id"] == category.id

    async def test_get_category_products_unauthenticated(
        self, async_client: AsyncClient, category_factory
    ):
        """Test getting category products without authentication."""
        category = await category_factory(name="Mobile Phones")

        response = await async_client.get(
            f"/api/v1/categories/{category.id}/products/"
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestCategoryEndpointIntegration:
    """Integration tests for category endpoints."""

    async def test_full_crud_workflow(
        self, async_client: AsyncClient, category_type_factory, auth_headers_system
    ):
        """Test complete CRUD workflow for categories."""
        # Create category type first
        category_type = await category_type_factory(name="Electronics")

        # Create
        create_data = {
            "name": "Mobile Phones",
            "description": "Mobile phones and accessories",
            "category_type_id": category_type.id,
            "sequence": 10
        }
        response = await async_client.post(
            "/api/v1/categories/", json=create_data, headers=auth_headers_system
        )
        assert response.status_code == 201
        created_data = response.json()["data"]
        category_id = created_data["id"]

        # Read individual
        response = await async_client.get(
            f"/api/v1/categories/{category_id}", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Mobile Phones"
        assert data["slug"] == "mobile-phones"
        assert data["sequence"] == 10
        assert data["category_type_id"] == category_type.id

        # Read list
        response = await async_client.get(
            "/api/v1/categories/", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "Mobile Phones"
        assert data[0]["slug"] == "mobile-phones"
        assert data[0]["sequence"] == 10

        # Update
        update_data = {
            "name": "Mobile Phones and Accessories",
            "description": "Updated description",
            "is_active": False
        }
        response = await async_client.put(
            f"/api/v1/categories/{category_id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Mobile Phones and Accessories"
        assert data["slug"] == "mobile-phones-and-accessories"
        assert data["description"] == "Updated description"
        assert data["is_active"] is False

        # Delete
        response = await async_client.delete(
            f"/api/v1/categories/{category_id}", headers=auth_headers_system
        )
        assert response.status_code == 204

        # Verify item is deleted
        response = await async_client.get(
            f"/api/v1/categories/{category_id}", headers=auth_headers_system
        )
        assert response.status_code == 404
        error = response.json()["error"]
        assert error["message"] == f"Category with id {category_id} not found"

    async def test_hierarchical_category_workflow(
        self, async_client: AsyncClient, category_type_factory, auth_headers_system
    ):
        """Test hierarchical category creation and management."""
        # Create category type
        category_type = await category_type_factory(name="Electronics")

        # Create parent category
        parent_data = {
            "name": "Mobile Phones",
            "category_type_id": category_type.id
        }
        response = await async_client.post(
            "/api/v1/categories/", json=parent_data, headers=auth_headers_system
        )
        assert response.status_code == 201
        parent_id = response.json()["data"]["id"]

        # Create child categories
        child1_data = {
            "name": "Smartphones",
            "parent_id": parent_id
        }
        response = await async_client.post(
            "/api/v1/categories/", json=child1_data, headers=auth_headers_system
        )
        assert response.status_code == 201
        child1_id = response.json()["data"]["id"]

        child2_data = {
            "name": "Feature Phones",
            "parent_id": parent_id
        }
        response = await async_client.post(
            "/api/v1/categories/", json=child2_data, headers=auth_headers_system
        )
        assert response.status_code == 201

        # Get children
        response = await async_client.get(
            f"/api/v1/categories/{parent_id}/children/", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        names = {item["name"] for item in data}
        assert names == {"Smartphones", "Feature Phones"}

        # Verify hierarchy in child category
        response = await async_client.get(
            f"/api/v1/categories/{child1_id}", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["full_path"]) == 2
        assert data["full_path"][0]["name"] == "Mobile Phones"
        assert data["full_path"][1]["name"] == "Smartphones"

        # Try to delete parent (should fail due to children)
        response = await async_client.delete(
            f"/api/v1/categories/{parent_id}", headers=auth_headers_system
        )
        assert response.status_code == 400
        error = response.json()["error"]
        assert "Cannot delete category. It has 2 child categories" in error["message"]

    async def test_category_with_products_workflow(
        self, async_client: AsyncClient, category_type_factory, product_factory,
        auth_headers_system
    ):
        """Test category workflow with associated products."""
        # Create category type and category
        category_type = await category_type_factory(name="Electronics")
        category_data = {
            "name": "Mobile Phones",
            "category_type_id": category_type.id
        }
        response = await async_client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers_system
        )
        assert response.status_code == 201
        category_id = response.json()["data"]["id"]

        # Create products using factory (simulating external creation)
        await product_factory(name="iPhone 15", category_id=category_id)
        await product_factory(name="Samsung Galaxy S24", category_id=category_id)

        # Get products by category
        response = await async_client.get(
            f"/api/v1/categories/{category_id}/products/", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        names = {item["name"] for item in data}
        assert names == {"iPhone 15", "Samsung Galaxy S24"}

        # Try to delete category (should fail due to products)
        response = await async_client.delete(
            f"/api/v1/categories/{category_id}", headers=auth_headers_system
        )
        assert response.status_code == 400
        error = response.json()["error"]
        assert "Cannot delete category. It has 2 products" in error["message"]

    async def test_full_crud_workflow_by_user(
        self, async_client: AsyncClient, category_type_factory,
        auth_headers_system, auth_headers_user
    ):
        """Test CRUD workflow with resource ownership by user vs system."""
        # Create category type first
        category_type = await category_type_factory(name="Electronics")

        # === CREATE PHASE ===
        # Create category by SYSTEM
        system_category_data = {
            "name": "Mobile Phones System",
            "description": "Category created by system",
            "category_type_id": category_type.id
        }
        response = await async_client.post(
            "/api/v1/categories/",
            json=system_category_data,
            headers=auth_headers_system
        )
        assert response.status_code == 201
        system_category_id = response.json()["data"]["id"]

        # Create category by USER
        user_category_data = {
            "name": "Mobile Phones User",
            "description": "Category created by user",
            "category_type_id": category_type.id
        }
        response = await async_client.post(
            "/api/v1/categories/",
            json=user_category_data,
            headers=auth_headers_user
        )
        assert response.status_code == 201
        user_category_id = response.json()["data"]["id"]

        # === READ PHASE ===
        # User can read both categories (system and their own)
        response = await async_client.get(
            f"/api/v1/categories/{system_category_id}", headers=auth_headers_user
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Mobile Phones System"

        response = await async_client.get(
            f"/api/v1/categories/{user_category_id}", headers=auth_headers_user
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Mobile Phones User"

        # === UPDATE PHASE ===
        # User tries to update SYSTEM category (should fail - ownership check)
        update_data = {"description": "Updated by user"}
        response = await async_client.put(
            f"/api/v1/categories/{system_category_id}",
            json=update_data,
            headers=auth_headers_user
        )
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

        # User updates their OWN category (should succeed)
        update_data = {"description": "Updated by user - own category"}
        response = await async_client.put(
            f"/api/v1/categories/{user_category_id}",
            json=update_data,
            headers=auth_headers_user
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["description"] == "Updated by user - own category"

        # System can update both categories (admin privileges)
        update_data = {"description": "Updated by system"}
        response = await async_client.put(
            f"/api/v1/categories/{system_category_id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        assert response.json()["data"]["description"] == "Updated by system"

        # === DELETE PHASE ===
        # User tries to delete SYSTEM category (should fail - ownership check)
        response = await async_client.delete(
            f"/api/v1/categories/{system_category_id}", headers=auth_headers_user
        )
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

        # User deletes their OWN category (should succeed)
        response = await async_client.delete(
            f"/api/v1/categories/{user_category_id}", headers=auth_headers_user
        )
        assert response.status_code == 204

        # Verify user's category is deleted
        response = await async_client.get(
            f"/api/v1/categories/{user_category_id}", headers=auth_headers_user
        )
        assert response.status_code == 404

        # System deletes their own category (should succeed)
        response = await async_client.delete(
            f"/api/v1/categories/{system_category_id}", headers=auth_headers_system
        )
        assert response.status_code == 204

        # Verify system category is deleted
        response = await async_client.get(
            f"/api/v1/categories/{system_category_id}", headers=auth_headers_system
        )
        assert response.status_code == 404
