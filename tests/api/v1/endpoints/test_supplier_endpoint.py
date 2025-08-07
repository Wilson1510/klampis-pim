from httpx import AsyncClient


class TestGetSuppliers:
    """Test cases for GET /suppliers/ endpoint."""

    async def test_get_suppliers_success(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test getting suppliers successfully."""
        # Create test data
        await supplier_factory(
            name="PT Maju Jaya",
            company_type="PT",
            email="maju@test.com",
            contact="081234567890"
        )
        await supplier_factory(
            name="CV Berkah",
            company_type="CV",
            email="berkah@test.com",
            contact="087654321098"
        )

        response = await async_client.get(
            "/api/v1/suppliers/", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
        names = {item["name"] for item in data}
        expected_names = {"PT Maju Jaya", "CV Berkah"}
        assert names == expected_names

        for item in data:
            assert "name" in item
            assert "slug" in item
            assert "company_type" in item
            assert "email" in item
            assert "contact" in item
            assert "address" in item

    async def test_get_suppliers_filter_by_name(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test filtering by name."""
        await supplier_factory(
            name="PT Electronics Indonesia",
            email="electronics@test.com",
            contact="081111111111"
        )
        await supplier_factory(
            name="CV Food Supplier",
            email="food@test.com",
            contact="082222222222"
        )

        response = await async_client.get(
            "/api/v1/suppliers/?name=Electronics", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "PT Electronics Indonesia"

    async def test_get_suppliers_filter_by_slug(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test filtering by slug."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )
        await supplier_factory(
            name="CV Berkah",
            email="berkah@test.com",
            contact="087654321098"
        )

        response = await async_client.get(
            f"/api/v1/suppliers/?slug={supplier.slug}", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["slug"] == supplier.slug

    async def test_get_suppliers_filter_by_company_type(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test filtering by company type."""
        await supplier_factory(
            name="PT Maju Jaya",
            company_type="PT",
            email="maju@test.com",
            contact="081234567890"
        )
        await supplier_factory(
            name="CV Berkah",
            company_type="CV",
            email="berkah@test.com",
            contact="087654321098"
        )

        response = await async_client.get(
            "/api/v1/suppliers/?company_type=PT", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["company_type"] == "PT"

    async def test_get_suppliers_filter_by_email(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test filtering by email."""
        await supplier_factory(
            name="PT Maju",
            email="info@majujaya.com",
            contact="081234567890"
        )
        await supplier_factory(
            name="CV Berkah",
            email="contact@berkah.com",
            contact="087654321098"
        )

        response = await async_client.get(
            "/api/v1/suppliers/?email=majujaya", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert "majujaya" in data[0]["email"]

    async def test_get_suppliers_filter_by_contact(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test filtering by contact."""
        await supplier_factory(
            name="PT Maju",
            contact="081234567890",
            email="maju@test.com"
        )
        await supplier_factory(
            name="CV Berkah",
            contact="087654321098",
            email="berkah@test.com"
        )

        response = await async_client.get(
            "/api/v1/suppliers/?contact=08123", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert "08123" in data[0]["contact"]

    async def test_get_suppliers_filter_by_is_active(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test filtering by is_active status."""
        await supplier_factory(
            name="Active Supplier",
            is_active=True,
            email="active@test.com",
            contact="081234567890"
        )
        await supplier_factory(
            name="Inactive Supplier",
            is_active=False,
            email="inactive@test.com",
            contact="087654321098"
        )

        # Test active filter
        response = await async_client.get(
            "/api/v1/suppliers/?is_active=true", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is True

        # Test inactive filter
        response = await async_client.get(
            "/api/v1/suppliers/?is_active=false", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is False

    async def test_get_suppliers_combined_filters(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test combining multiple filters."""
        await supplier_factory(
            name="PT Electronics",
            company_type="PT",
            is_active=True,
            email="electronics@test.com",
            contact="081234567890"
        )
        await supplier_factory(
            name="CV Food",
            company_type="CV",
            is_active=False,
            email="food@test.com",
            contact="087654321098"
        )

        response = await async_client.get(
            "/api/v1/suppliers/?company_type=PT&is_active=true",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["company_type"] == "PT"
        assert data[0]["is_active"] is True

    async def test_get_suppliers_by_user(
        self, async_client: AsyncClient, supplier_factory, auth_headers_user
    ):
        """Test getting suppliers by user."""
        await supplier_factory(
            name="PT Maju Jaya",
            company_type="PT",
            email="maju@test.com",
            contact="081234567890"
        )
        await supplier_factory(
            name="CV Berkah",
            company_type="CV",
            email="berkah@test.com",
            contact="087654321098"
        )

        response = await async_client.get(
            "/api/v1/suppliers/", headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
        names = {item["name"] for item in data}
        expected_names = {"PT Maju Jaya", "CV Berkah"}
        assert names == expected_names

        for item in data:
            assert "name" in item
            assert "slug" in item
            assert "company_type" in item
            assert "email" in item
            assert "contact" in item

    async def test_get_suppliers_unauthenticated(
        self, async_client: AsyncClient
    ):
        """Test getting suppliers without authentication."""
        response = await async_client.get("/api/v1/suppliers/")
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestCreateSupplier:
    """Test cases for POST /suppliers/ endpoint."""

    async def test_create_supplier_success(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating supplier successfully."""
        supplier_data = {
            "name": "PT Maju Jaya",
            "company_type": "PT",
            "address": "Jl. Sudirman No. 123",
            "contact": "081234567890",
            "email": "info@majujaya.com"
        }

        response = await async_client.post(
            "/api/v1/suppliers/", json=supplier_data, headers=auth_headers_system
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "PT Maju Jaya"
        assert data["company_type"] == "PT"
        assert data["address"] == "Jl. Sudirman No. 123"
        assert data["contact"] == "081234567890"
        assert data["email"] == "info@majujaya.com"
        assert data["slug"] == "pt-maju-jaya"

    async def test_create_supplier_duplicate_name(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test creating supplier with duplicate name."""
        await supplier_factory(
            name="PT Maju Jaya",
            email="existing@test.com",
            contact="081234567890"
        )

        supplier_data = {
            "name": "PT Maju Jaya",
            "company_type": "PT",
            "contact": "081234567891",
            "email": "info2@majujaya.com"
        }
        response = await async_client.post(
            "/api/v1/suppliers/", json=supplier_data, headers=auth_headers_system
        )
        error = response.json()["error"]

        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Supplier with name 'PT Maju Jaya' already exists"
        )
        assert error["details"] is None

    async def test_create_supplier_duplicate_email(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test creating supplier with duplicate email."""
        await supplier_factory(
            name="PT Existing",
            email="info@majujaya.com",
            contact="081234567890"
        )

        supplier_data = {
            "name": "PT Different Name",
            "company_type": "PT",
            "contact": "081234567891",
            "email": "info@majujaya.com"
        }
        response = await async_client.post(
            "/api/v1/suppliers/", json=supplier_data, headers=auth_headers_system
        )
        error = response.json()["error"]

        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Supplier with email 'info@majujaya.com' already exists"
        )
        assert error["details"] is None

    async def test_create_supplier_duplicate_contact(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test creating supplier with duplicate contact."""
        await supplier_factory(
            name="PT Existing",
            email="existing@test.com",
            contact="081234567890"
        )

        supplier_data = {
            "name": "PT Different Name",
            "company_type": "PT",
            "contact": "081234567890",
            "email": "different@email.com"
        }
        response = await async_client.post(
            "/api/v1/suppliers/", json=supplier_data, headers=auth_headers_system
        )
        error = response.json()["error"]

        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Supplier with contact '081234567890' already exists"
        )
        assert error["details"] is None

    async def test_create_supplier_by_user(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test creating supplier by user."""
        supplier_data = {
            "name": "PT Maju Jaya",
            "company_type": "PT",
            "address": "Jl. Sudirman No. 123",
            "contact": "081234567890",
            "email": "info@majujaya.com"
        }

        response = await async_client.post(
            "/api/v1/suppliers/", json=supplier_data, headers=auth_headers_user
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "PT Maju Jaya"
        assert data["company_type"] == "PT"
        assert data["contact"] == "081234567890"
        assert data["email"] == "info@majujaya.com"

    async def test_create_supplier_unauthenticated(
        self, async_client: AsyncClient
    ):
        """Test creating supplier without authentication."""
        supplier_data = {
            "name": "PT Maju Jaya",
            "company_type": "PT",
            "contact": "081234567890",
            "email": "info@majujaya.com"
        }

        response = await async_client.post(
            "/api/v1/suppliers/", json=supplier_data
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestGetSupplier:
    """Test cases for GET /suppliers/{id} endpoint."""

    async def test_get_supplier_success(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test getting supplier by ID successfully."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )

        response = await async_client.get(
            f"/api/v1/suppliers/{supplier.id}", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == supplier.id
        assert data["name"] == "PT Maju Jaya"
        assert data["slug"] == supplier.slug

    async def test_get_supplier_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test getting non-existent supplier."""
        response = await async_client.get(
            "/api/v1/suppliers/999", headers=auth_headers_system
        )
        error = response.json()["error"]

        assert response.status_code == 404
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Supplier with id 999 not found"
        assert error["details"] is None

    async def test_get_supplier_by_user(
        self, async_client: AsyncClient, supplier_factory, auth_headers_user
    ):
        """Test getting supplier by ID by user."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )

        response = await async_client.get(
            f"/api/v1/suppliers/{supplier.id}", headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == supplier.id
        assert data["name"] == "PT Maju Jaya"
        assert data["slug"] == supplier.slug

    async def test_get_supplier_unauthenticated(
        self, async_client: AsyncClient, supplier_factory
    ):
        """Test getting supplier by ID without authentication."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )

        response = await async_client.get(
            f"/api/v1/suppliers/{supplier.id}"
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestUpdateSupplier:
    """Test cases for PUT /suppliers/{id} endpoint."""

    async def test_update_supplier_success(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test updating supplier successfully."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )

        update_data = {
            "name": "PT Maju Jaya Sejahtera",
            "address": "Jl. Thamrin No. 456"
        }
        response = await async_client.put(
            f"/api/v1/suppliers/{supplier.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == supplier.id
        assert data["name"] == "PT Maju Jaya Sejahtera"
        assert data["address"] == "Jl. Thamrin No. 456"
        assert data["slug"] == "pt-maju-jaya-sejahtera"

    async def test_update_supplier_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test updating non-existent supplier."""
        update_data = {"name": "Updated Name"}
        response = await async_client.put(
            "/api/v1/suppliers/999", json=update_data, headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Supplier with id 999 not found"
        assert error["details"] is None

    async def test_update_supplier_duplicate_name(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test updating supplier with duplicate name."""
        await supplier_factory(
            name="PT Existing",
            email="existing@test.com",
            contact="081234567890"
        )
        supplier2 = await supplier_factory(
            name="PT Different",
            email="different@test.com",
            contact="087654321098"
        )

        update_data = {"name": "PT Existing"}
        response = await async_client.put(
            f"/api/v1/suppliers/{supplier2.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Supplier with name 'PT Existing' already exists"
        )
        assert error["details"] is None

    async def test_update_supplier_duplicate_email(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test updating supplier with duplicate email."""
        await supplier_factory(
            name="PT Existing",
            email="existing@email.com",
            contact="081234567890"
        )
        supplier2 = await supplier_factory(
            name="PT Different",
            email="different@email.com",
            contact="087654321098"
        )

        update_data = {"email": "existing@email.com"}
        response = await async_client.put(
            f"/api/v1/suppliers/{supplier2.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Supplier with email 'existing@email.com' already exists"
        )
        assert error["details"] is None

    async def test_update_supplier_duplicate_contact(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test updating supplier with duplicate contact."""
        await supplier_factory(
            name="PT Existing",
            email="existing@test.com",
            contact="081234567890"
        )
        supplier2 = await supplier_factory(
            name="PT Different",
            email="different@email.com",
            contact="087654321098"
        )

        update_data = {"contact": "081234567890"}
        response = await async_client.put(
            f"/api/v1/suppliers/{supplier2.id}",
            json=update_data,
            headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Supplier with contact '081234567890' already exists"
        )
        assert error["details"] is None

    async def test_update_supplier_by_user(
        self, async_client: AsyncClient, supplier_factory, auth_headers_user
    ):
        """Test updating supplier by user."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )

        update_data = {
            "name": "PT Maju Jaya Sejahtera",
            "address": "Jl. Thamrin No. 456"
        }
        response = await async_client.put(
            f"/api/v1/suppliers/{supplier.id}",
            json=update_data,
            headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

    async def test_update_supplier_unauthenticated(
        self, async_client: AsyncClient, supplier_factory
    ):
        """Test updating supplier without authentication."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )

        update_data = {"name": "PT Maju Jaya Sejahtera"}
        response = await async_client.put(
            f"/api/v1/suppliers/{supplier.id}", json=update_data
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestDeleteSupplier:
    """Test cases for DELETE /suppliers/{id} endpoint."""

    async def test_delete_supplier_success(
        self, async_client: AsyncClient, supplier_factory, auth_headers_system
    ):
        """Test deleting supplier successfully."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )

        response = await async_client.delete(
            f"/api/v1/suppliers/{supplier.id}", headers=auth_headers_system
        )

        assert response.status_code == 204

    async def test_delete_supplier_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test deleting non-existent supplier."""
        response = await async_client.delete(
            "/api/v1/suppliers/999", headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Supplier with id 999 not found"
        assert error["details"] is None

    async def test_delete_supplier_with_products(
        self, async_client: AsyncClient, supplier_factory, product_factory,
        auth_headers_system
    ):
        """Test deleting supplier that has associated products."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )

        # Create a product under this supplier
        await product_factory(
            name="Test Product",
            supplier=supplier
        )

        response = await async_client.delete(
            f"/api/v1/suppliers/{supplier.id}", headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Cannot delete supplier. "
            "It has 1 products"
        )
        assert error["details"] is None

    async def test_delete_supplier_by_user(
        self, async_client: AsyncClient, supplier_factory, auth_headers_user
    ):
        """Test deleting supplier by user."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )

        response = await async_client.delete(
            f"/api/v1/suppliers/{supplier.id}", headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

    async def test_delete_supplier_unauthenticated(
        self, async_client: AsyncClient, supplier_factory
    ):
        """Test deleting supplier without authentication."""
        supplier = await supplier_factory(
            name="PT Maju Jaya",
            email="maju@test.com",
            contact="081234567890"
        )

        response = await async_client.delete(
            f"/api/v1/suppliers/{supplier.id}"
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestGetSupplierProducts:
    """Test cases for GET /suppliers/{id}/products/ endpoint."""

    async def test_get_supplier_products_success(
        self, async_client: AsyncClient, supplier_factory, product_factory,
        auth_headers_system
    ):
        """Test getting products by supplier successfully."""
        supplier = await supplier_factory(
            name="PT Electronics",
            email="electronics@test.com",
            contact="081234567890"
        )
        await product_factory(
            name="Smartphone", supplier=supplier
        )
        await product_factory(
            name="Laptop", supplier=supplier
        )

        # Create product with different supplier to ensure filtering
        other_supplier = await supplier_factory(
            name="PT Food",
            email="food@test.com",
            contact="087654321098"
        )
        await product_factory(name="Rice", supplier=other_supplier)

        response = await async_client.get(
            f"/api/v1/suppliers/{supplier.id}/products/",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        names = {item["name"] for item in data}
        expected_names = {"Smartphone", "Laptop"}
        assert names == expected_names

        for item in data:
            assert "name" in item
            assert "slug" in item
            assert "description" in item
            assert "category_id" in item
            assert "supplier_id" in item
            assert "full_path" in item
            assert item["supplier_id"] == supplier.id

    async def test_get_supplier_products_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test getting products for non-existent supplier."""
        response = await async_client.get(
            "/api/v1/suppliers/999/products/", headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Supplier with id 999 not found"
        assert error["details"] is None

    async def test_get_supplier_products_by_user(
        self, async_client: AsyncClient, supplier_factory, product_factory,
        auth_headers_user
    ):
        """Test getting products by supplier by user."""
        supplier = await supplier_factory(
            name="PT Electronics",
            email="electronics@test.com",
            contact="081234567890"
        )
        await product_factory(
            name="Smartphone", supplier=supplier
        )
        await product_factory(
            name="Laptop", supplier=supplier
        )

        response = await async_client.get(
            f"/api/v1/suppliers/{supplier.id}/products/",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        names = {item["name"] for item in data}
        expected_names = {"Smartphone", "Laptop"}
        assert names == expected_names

        for item in data:
            assert item["supplier_id"] == supplier.id

    async def test_get_supplier_products_unauthenticated(
        self, async_client: AsyncClient, supplier_factory
    ):
        """Test getting products by supplier without authentication."""
        supplier = await supplier_factory(
            name="PT Electronics",
            email="electronics@test.com",
            contact="081234567890"
        )

        response = await async_client.get(
            f"/api/v1/suppliers/{supplier.id}/products/"
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestSupplierEndpointIntegration:
    """Integration tests for supplier endpoints."""

    async def test_full_crud_workflow(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test complete CRUD workflow for suppliers."""
        # Create
        create_data = {
            "name": "PT Maju Jaya",
            "company_type": "PT",
            "address": "Jl. Sudirman No. 123",
            "contact": "081234567890",
            "email": "info@majujaya.com"
        }
        response = await async_client.post(
            "/api/v1/suppliers/", json=create_data, headers=auth_headers_system
        )
        assert response.status_code == 201
        created_data = response.json()["data"]
        supplier_id = created_data["id"]

        # Read individual
        response = await async_client.get(
            f"/api/v1/suppliers/{supplier_id}", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "PT Maju Jaya"
        assert data["slug"] == "pt-maju-jaya"
        assert data["company_type"] == "PT"
        assert data["contact"] == "081234567890"
        assert data["email"] == "info@majujaya.com"

        # Read list
        response = await async_client.get(
            "/api/v1/suppliers/", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "PT Maju Jaya"

        # Update
        update_data = {
            "name": "PT Maju Jaya Sejahtera",
            "address": "Jl. Thamrin No. 456",
            "is_active": False
        }
        response = await async_client.put(
            f"/api/v1/suppliers/{supplier_id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "PT Maju Jaya Sejahtera"
        assert data["slug"] == "pt-maju-jaya-sejahtera"
        assert data["address"] == "Jl. Thamrin No. 456"
        assert data["is_active"] is False

        # Delete
        response = await async_client.delete(
            f"/api/v1/suppliers/{supplier_id}", headers=auth_headers_system
        )
        assert response.status_code == 204

        # Verify item is deleted
        response = await async_client.get(
            f"/api/v1/suppliers/{supplier_id}", headers=auth_headers_system
        )
        assert response.status_code == 404
        error = response.json()["error"]
        assert error["message"] == f"Supplier with id {supplier_id} not found"

    async def test_supplier_with_products_workflow(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test supplier workflow with associated products."""
        # Create supplier
        create_data = {
            "name": "PT Electronics",
            "company_type": "PT",
            "contact": "081234567890",
            "email": "info@electronics.com"
        }
        response = await async_client.post(
            "/api/v1/suppliers/", json=create_data, headers=auth_headers_system
        )
        assert response.status_code == 201
        supplier_id = response.json()["data"]["id"]

        # Create products using factory (simulating external creation)
        await product_factory(
            name="Smartphone", supplier_id=supplier_id
        )
        await product_factory(
            name="Laptop", supplier_id=supplier_id
        )

        # Get products by supplier
        response = await async_client.get(
            f"/api/v1/suppliers/{supplier_id}/products/",
            headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        assert data[0]["name"] == "Smartphone"
        assert data[1]["name"] == "Laptop"

        # Try to delete supplier (should fail)
        response = await async_client.delete(
            f"/api/v1/suppliers/{supplier_id}", headers=auth_headers_system
        )
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["message"] == (
            "Cannot delete supplier. "
            "It has 2 products"
        )
        assert error["details"] is None

    async def test_full_crud_workflow_by_user(
        self, async_client: AsyncClient, auth_headers_system, auth_headers_user
    ):
        """Test CRUD workflow with resource ownership by user vs system."""
        # === CREATE PHASE ===
        # Create supplier by SYSTEM
        system_supplier_data = {
            "name": "PT Electronics System",
            "company_type": "PT",
            "contact": "081111111111",
            "email": "system@electronics.com"
        }
        response = await async_client.post(
            "/api/v1/suppliers/",
            json=system_supplier_data,
            headers=auth_headers_system
        )
        assert response.status_code == 201
        system_supplier_id = response.json()["data"]["id"]

        # Create supplier by USER
        user_supplier_data = {
            "name": "PT Electronics User",
            "company_type": "PT",
            "contact": "082222222222",
            "email": "user@electronics.com"
        }
        response = await async_client.post(
            "/api/v1/suppliers/",
            json=user_supplier_data,
            headers=auth_headers_user
        )
        assert response.status_code == 201
        user_supplier_id = response.json()["data"]["id"]

        # === READ PHASE ===
        # User can read both suppliers (system and their own)
        response = await async_client.get(
            f"/api/v1/suppliers/{system_supplier_id}", headers=auth_headers_user
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "PT Electronics System"

        response = await async_client.get(
            f"/api/v1/suppliers/{user_supplier_id}", headers=auth_headers_user
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "PT Electronics User"

        # === UPDATE PHASE ===
        # User tries to update SYSTEM supplier (should fail - ownership check)
        update_data = {"address": "Updated by user"}
        response = await async_client.put(
            f"/api/v1/suppliers/{system_supplier_id}",
            json=update_data,
            headers=auth_headers_user
        )
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

        # User updates their OWN supplier (should succeed)
        update_data = {"address": "Updated by user - own supplier"}
        response = await async_client.put(
            f"/api/v1/suppliers/{user_supplier_id}",
            json=update_data,
            headers=auth_headers_user
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["address"] == "Updated by user - own supplier"

        # System can update both suppliers (admin privileges)
        update_data = {"address": "Updated by system"}
        response = await async_client.put(
            f"/api/v1/suppliers/{system_supplier_id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        assert response.json()["data"]["address"] == "Updated by system"

        # === DELETE PHASE ===
        # User tries to delete SYSTEM supplier (should fail - ownership check)
        response = await async_client.delete(
            f"/api/v1/suppliers/{system_supplier_id}", headers=auth_headers_user
        )
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

        # User deletes their OWN supplier (should succeed)
        response = await async_client.delete(
            f"/api/v1/suppliers/{user_supplier_id}", headers=auth_headers_user
        )
        assert response.status_code == 204

        # Verify user's supplier is deleted
        response = await async_client.get(
            f"/api/v1/suppliers/{user_supplier_id}", headers=auth_headers_user
        )
        assert response.status_code == 404

        # System deletes their own supplier (should succeed)
        response = await async_client.delete(
            f"/api/v1/suppliers/{system_supplier_id}", headers=auth_headers_system
        )
        assert response.status_code == 204

        # Verify system supplier is deleted
        response = await async_client.get(
            f"/api/v1/suppliers/{system_supplier_id}", headers=auth_headers_system
        )
        assert response.status_code == 404
