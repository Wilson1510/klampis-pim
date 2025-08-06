from httpx import AsyncClient


class TestGetProducts:
    """Test cases for GET /products/ endpoint."""

    async def test_get_products_success(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test getting products successfully."""
        # Create test data
        await product_factory(name="iPhone 15")
        await product_factory(name="Samsung Galaxy S24")

        response = await async_client.get(
            "/api/v1/products/", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
        names = {item["name"] for item in data}
        expected_names = {"iPhone 15", "Samsung Galaxy S24"}
        assert names == expected_names

        for item in data:
            assert "name" in item
            assert "slug" in item
            assert "description" in item
            assert "category_id" in item
            assert "supplier_id" in item
            assert "full_path" in item
            assert "images" in item

    async def test_get_products_filter_by_name(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test filtering by name."""
        await product_factory(name="iPhone 15 Pro Max")
        await product_factory(name="Samsung Galaxy S24 Ultra")

        response = await async_client.get(
            "/api/v1/products/?name=iPhone", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "iPhone 15 Pro Max"

    async def test_get_products_filter_by_slug(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test filtering by slug."""
        await product_factory(name="iPhone 15")
        await product_factory(name="Samsung Galaxy S24")

        response = await async_client.get(
            "/api/v1/products/?slug=iphone-15", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["slug"] == "iphone-15"

    async def test_get_products_filter_by_category_id(
        self, async_client: AsyncClient, product_factory, category_factory,
        auth_headers_system
    ):
        """Test filtering by category_id."""
        electronics_category = await category_factory(name="Electronics")
        food_category = await category_factory(name="Food")

        await product_factory(
            name="iPhone 15",
            category=electronics_category
        )
        await product_factory(
            name="Coca Cola",
            category=food_category
        )

        response = await async_client.get(
            f"/api/v1/products/?category_id={electronics_category.id}",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["category_id"] == electronics_category.id

    async def test_get_products_filter_by_supplier_id(
        self, async_client: AsyncClient, product_factory, supplier_factory,
        auth_headers_system
    ):
        """Test filtering by supplier_id."""
        apple_supplier = await supplier_factory(
            name="Apple Inc",
            contact="1234567890",
            email="apple@example.com"
        )
        samsung_supplier = await supplier_factory(
            name="Samsung Corp",
            contact="1234567891",
            email="samsung@example.com"
        )

        await product_factory(
            name="iPhone 15",
            supplier=apple_supplier
        )
        await product_factory(
            name="Galaxy S24",
            supplier=samsung_supplier
        )

        response = await async_client.get(
            f"/api/v1/products/?supplier_id={apple_supplier.id}",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["supplier_id"] == apple_supplier.id

    async def test_get_products_filter_by_is_active(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test filtering by is_active status."""
        await product_factory(name="Active Product", is_active=True)
        await product_factory(name="Inactive Product", is_active=False)

        # Test active filter
        response = await async_client.get(
            "/api/v1/products/?is_active=true", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is True

        # Test inactive filter
        response = await async_client.get(
            "/api/v1/products/?is_active=false", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is False

    async def test_get_products_combined_filters(
        self,
        async_client: AsyncClient,
        product_factory,
        category_factory,
        supplier_factory,
        auth_headers_system
    ):
        """Test combining multiple filters."""
        electronics_category = await category_factory(name="Electronics")
        food_category = await category_factory(name="Food")
        apple_supplier = await supplier_factory(name="Apple Inc")

        await product_factory(
            name="iPhone 15",
            category=electronics_category,
            supplier=apple_supplier,
            is_active=True
        )
        await product_factory(
            name="Coca Cola",
            category=food_category,
            supplier=apple_supplier,
            is_active=False
        )

        response = await async_client.get(
            f"/api/v1/products/?category_id={electronics_category.id}"
            f"&supplier_id={apple_supplier.id}&is_active=true",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["category_id"] == electronics_category.id
        assert data[0]["supplier_id"] == apple_supplier.id
        assert data[0]["is_active"] is True

    async def test_get_products_by_user(
        self, async_client: AsyncClient, product_factory, auth_headers_user
    ):
        """Test getting products by user."""
        await product_factory(name="iPhone 15")
        await product_factory(name="Samsung Galaxy S24")

        response = await async_client.get(
            "/api/v1/products/", headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
        names = {item["name"] for item in data}
        expected_names = {"iPhone 15", "Samsung Galaxy S24"}
        assert names == expected_names

        for item in data:
            assert "name" in item
            assert "slug" in item
            assert "description" in item
            assert "category_id" in item
            assert "supplier_id" in item

    async def test_get_products_unauthenticated(
        self, async_client: AsyncClient
    ):
        """Test getting products without authentication."""
        response = await async_client.get("/api/v1/products/")
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestCreateProduct:
    """Test cases for POST /products/ endpoint."""

    async def test_create_product_success(
        self, async_client: AsyncClient, category_factory, supplier_factory,
        auth_headers_system
    ):
        """Test creating product successfully."""
        category = await category_factory(name="Electronics")
        supplier = await supplier_factory(name="Apple Inc")

        product_data = {
            "name": "iPhone 15",
            "description": "Latest iPhone model",
            "category_id": category.id,
            "supplier_id": supplier.id
        }

        response = await async_client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers_system
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "iPhone 15"
        assert data["slug"] == "iphone-15"
        assert data["category_id"] == category.id
        assert data["supplier_id"] == supplier.id
        assert len(data['full_path']) == 2  # Category + Product

    async def test_create_product_duplicate_name(
        self,
        async_client: AsyncClient,
        product_factory,
        category_factory,
        supplier_factory,
        auth_headers_system
    ):
        """Test creating product with duplicate name."""
        category = await category_factory(name="Electronics")
        supplier = await supplier_factory(name="Apple Inc")

        await product_factory(
            name="iPhone 15",
            category=category,
            supplier=supplier
        )

        product_data = {
            "name": "iPhone 15",
            "category_id": category.id,
            "supplier_id": supplier.id
        }
        response = await async_client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Product with name 'iPhone 15' already exists"
        )
        assert error["details"] is None

    async def test_create_product_by_user(
        self, async_client: AsyncClient, category_factory, supplier_factory,
        auth_headers_user
    ):
        """Test creating product by user."""
        category = await category_factory(name="Electronics")
        supplier = await supplier_factory(name="Apple Inc")

        product_data = {
            "name": "iPhone 15",
            "description": "Latest iPhone model",
            "category_id": category.id,
            "supplier_id": supplier.id
        }

        response = await async_client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers_user
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "iPhone 15"
        assert data["slug"] == "iphone-15"
        assert data["category_id"] == category.id
        assert data["supplier_id"] == supplier.id

    async def test_create_product_unauthenticated(
        self, async_client: AsyncClient
    ):
        """Test creating product without authentication."""
        product_data = {
            "name": "iPhone 15",
            "description": "Latest iPhone model",
            "category_id": 1,
            "supplier_id": 1
        }

        response = await async_client.post(
            "/api/v1/products/", json=product_data
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestGetProduct:
    """Test cases for GET /products/{id} endpoint."""

    async def test_get_product_success(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test getting product by ID successfully."""
        product = await product_factory(name="iPhone 15")

        response = await async_client.get(
            f"/api/v1/products/{product.id}", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == product.id
        assert data["name"] == "iPhone 15"
        assert data["slug"] == product.slug
        assert len(data['full_path']) == 2  # Category + Product

    async def test_get_product_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test getting non-existent product."""
        response = await async_client.get(
            "/api/v1/products/999", headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Product with id 999 not found"
        assert error["details"] is None

    async def test_get_product_by_user(
        self, async_client: AsyncClient, product_factory, auth_headers_user
    ):
        """Test getting product by ID by user."""
        product = await product_factory(name="iPhone 15")

        response = await async_client.get(
            f"/api/v1/products/{product.id}", headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == product.id
        assert data["name"] == "iPhone 15"
        assert data["slug"] == product.slug

    async def test_get_product_unauthenticated(
        self, async_client: AsyncClient, product_factory
    ):
        """Test getting product by ID without authentication."""
        product = await product_factory(name="iPhone 15")

        response = await async_client.get(
            f"/api/v1/products/{product.id}"
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestUpdateProduct:
    """Test cases for PUT /products/{id} endpoint."""

    async def test_update_product_success(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test updating product successfully."""
        product = await product_factory(name="iPhone 15")

        update_data = {
            "name": "iPhone 15 Pro",
            "description": "Updated description"
        }
        response = await async_client.put(
            f"/api/v1/products/{product.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == product.id
        assert data["name"] == "iPhone 15 Pro"
        assert data["slug"] == "iphone-15-pro"
        assert data["description"] == "Updated description"

    async def test_update_product_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test updating non-existent product."""
        update_data = {"name": "Updated Name"}
        response = await async_client.put(
            "/api/v1/products/999",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Product with id 999 not found"
        assert error["details"] is None

    async def test_update_product_duplicate_name(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test updating product with duplicate name."""
        await product_factory(name="iPhone 15")
        product2 = await product_factory(name="Galaxy S24")

        update_data = {"name": "iPhone 15"}
        response = await async_client.put(
            f"/api/v1/products/{product2.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Product with name 'iPhone 15' already exists"
        )
        assert error["details"] is None

    async def test_update_product_by_user(
        self, async_client: AsyncClient, product_factory, auth_headers_user
    ):
        """Test updating product by user."""
        product = await product_factory(name="iPhone 15")

        update_data = {
            "name": "iPhone 15 Pro",
            "description": "Updated description"
        }
        response = await async_client.put(
            f"/api/v1/products/{product.id}",
            json=update_data,
            headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

    async def test_update_product_unauthenticated(
        self, async_client: AsyncClient, product_factory
    ):
        """Test updating product without authentication."""
        product = await product_factory(name="iPhone 15")

        update_data = {"name": "iPhone 15 Pro"}
        response = await async_client.put(
            f"/api/v1/products/{product.id}",
            json=update_data
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestDeleteProduct:
    """Test cases for DELETE /products/{id} endpoint."""

    async def test_delete_product_success(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test deleting product successfully."""
        product = await product_factory(name="iPhone 15")

        response = await async_client.delete(
            f"/api/v1/products/{product.id}", headers=auth_headers_system
        )

        assert response.status_code == 204

    async def test_delete_product_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test deleting non-existent product."""
        response = await async_client.delete(
            "/api/v1/products/999", headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Product with id 999 not found"
        assert error["details"] is None

    async def test_delete_product_with_skus(
        self, async_client: AsyncClient, product_factory, sku_factory,
        auth_headers_system
    ):
        """Test deleting product that has SKUs."""
        product = await product_factory(name="iPhone 15")

        # Create a SKU for this product
        await sku_factory(
            name="iPhone 15 128GB",
            product=product
        )

        response = await async_client.delete(
            f"/api/v1/products/{product.id}", headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert "Cannot delete product. It has 1 SKUs" in error["message"]
        assert error["details"] is None

    async def test_delete_product_by_user(
        self, async_client: AsyncClient, product_factory, auth_headers_user
    ):
        """Test deleting product by user."""
        product = await product_factory(name="iPhone 15")

        response = await async_client.delete(
            f"/api/v1/products/{product.id}", headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

    async def test_delete_product_unauthenticated(
        self, async_client: AsyncClient, product_factory
    ):
        """Test deleting product without authentication."""
        product = await product_factory(name="iPhone 15")

        response = await async_client.delete(
            f"/api/v1/products/{product.id}"
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestGetProductSkus:
    """Test cases for GET /products/{id}/skus/ endpoint."""

    async def test_get_product_skus_success(
        self, async_client: AsyncClient, product_factory, sku_factory,
        auth_headers_system
    ):
        """Test getting product SKUs successfully."""
        product = await product_factory(name="iPhone 15")
        await sku_factory(name="iPhone 15 128GB", product=product)
        await sku_factory(name="iPhone 15 256GB", product=product)

        # Create SKU with different product to ensure filtering
        other_product = await product_factory(name="Galaxy S24")
        await sku_factory(name="Galaxy S24 128GB", product=other_product)

        response = await async_client.get(
            f"/api/v1/products/{product.id}/skus/",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        names = {item["name"] for item in data}
        expected_names = {"iPhone 15 128GB", "iPhone 15 256GB"}
        assert names == expected_names

        for item in data:
            assert item["product_id"] == product.id
            assert "name" in item
            assert "slug" in item
            assert "description" in item
            assert "sku_number" in item
            assert "sku_attribute_values" in item
            assert "price_details" in item

    async def test_get_product_skus_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test getting SKUs for non-existent product."""
        response = await async_client.get(
            "/api/v1/products/999/skus/", headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Product with id 999 not found"
        assert error["details"] is None

    async def test_get_product_skus_by_user(
        self, async_client: AsyncClient, product_factory, sku_factory,
        auth_headers_user
    ):
        """Test getting product SKUs by user."""
        product = await product_factory(name="iPhone 15")
        await sku_factory(name="iPhone 15 128GB", product=product)
        await sku_factory(name="iPhone 15 256GB", product=product)

        response = await async_client.get(
            f"/api/v1/products/{product.id}/skus/",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        names = {item["name"] for item in data}
        expected_names = {"iPhone 15 128GB", "iPhone 15 256GB"}
        assert names == expected_names

        for item in data:
            assert item["product_id"] == product.id
            assert "name" in item
            assert "slug" in item
            assert "description" in item
            assert "sku_number" in item

    async def test_get_product_skus_unauthenticated(
        self, async_client: AsyncClient, product_factory
    ):
        """Test getting product SKUs without authentication."""
        product = await product_factory(name="iPhone 15")

        response = await async_client.get(
            f"/api/v1/products/{product.id}/skus/"
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestProductEndpointIntegration:
    """Integration tests for product endpoints."""

    async def test_full_crud_workflow(
        self, async_client: AsyncClient, category_factory, supplier_factory,
        auth_headers_system
    ):
        """Test complete CRUD workflow for products."""
        # Create dependencies first
        category = await category_factory(name="Electronics")
        supplier = await supplier_factory(name="Apple Inc")

        # Create
        create_data = {
            "name": "iPhone 15",
            "description": "Latest iPhone model",
            "category_id": category.id,
            "supplier_id": supplier.id,
            "sequence": 10
        }
        response = await async_client.post(
            "/api/v1/products/", json=create_data, headers=auth_headers_system
        )
        assert response.status_code == 201
        created_data = response.json()["data"]
        product_id = created_data["id"]

        # Read individual
        response = await async_client.get(
            f"/api/v1/products/{product_id}", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "iPhone 15"
        assert data["slug"] == "iphone-15"
        assert data["sequence"] == 10
        assert data["category_id"] == category.id
        assert data["supplier_id"] == supplier.id

        # Read list
        response = await async_client.get(
            "/api/v1/products/", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "iPhone 15"
        assert data[0]["slug"] == "iphone-15"
        assert data[0]["sequence"] == 10

        # Update
        update_data = {
            "name": "iPhone 15 Pro",
            "description": "Updated description",
            "is_active": False
        }
        response = await async_client.put(
            f"/api/v1/products/{product_id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "iPhone 15 Pro"
        assert data["slug"] == "iphone-15-pro"
        assert data["description"] == "Updated description"
        assert data["is_active"] is False

        # Delete
        response = await async_client.delete(
            f"/api/v1/products/{product_id}", headers=auth_headers_system
        )
        assert response.status_code == 204

        # Verify item is deleted
        response = await async_client.get(
            f"/api/v1/products/{product_id}", headers=auth_headers_system
        )
        assert response.status_code == 404
        error = response.json()["error"]
        assert error["message"] == f"Product with id {product_id} not found"

    async def test_product_with_skus_workflow(
        self, async_client: AsyncClient, product_factory, sku_factory,
        auth_headers_system
    ):
        """Test product workflow with associated SKUs."""
        # Create product
        product = await product_factory(name="iPhone 15")

        # Create SKUs using factory (simulating external creation)
        await sku_factory(name="iPhone 15 128GB", product=product)
        await sku_factory(name="iPhone 15 256GB", product=product)

        # Get SKUs by product
        response = await async_client.get(
            f"/api/v1/products/{product.id}/skus/", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        names = {item["name"] for item in data}
        assert names == {"iPhone 15 128GB", "iPhone 15 256GB"}

        # Try to delete product (should fail due to SKUs)
        response = await async_client.delete(
            f"/api/v1/products/{product.id}", headers=auth_headers_system
        )
        assert response.status_code == 400
        error = response.json()["error"]
        assert "Cannot delete product. It has 2 SKUs" in error["message"]
