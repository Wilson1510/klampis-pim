from httpx import AsyncClient


class TestGetPricelists:
    """Test cases for GET /pricelists/ endpoint."""

    async def test_get_pricelists_success(
        self, async_client: AsyncClient, pricelist_factory
    ):
        """Test getting pricelists successfully."""
        # Create test data
        await pricelist_factory(name="Standard Price", description="Standard pricing")
        await pricelist_factory(name="Premium Price", description="Premium pricing")

        response = await async_client.get("/api/v1/pricelists/")

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
        names = {item["name"] for item in data}
        expected_names = {"Standard Price", "Premium Price"}
        assert names == expected_names

        for item in data:
            assert "name" in item
            assert "code" in item
            assert "description" in item

    async def test_get_pricelists_filter_by_name(
        self, async_client: AsyncClient, pricelist_factory
    ):
        """Test filtering by name."""
        await pricelist_factory(name="Standard Price List")
        await pricelist_factory(name="Premium Price List")

        response = await async_client.get("/api/v1/pricelists/?name=Standard")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "Standard Price List"

    async def test_get_pricelists_filter_by_code(
        self, async_client: AsyncClient, pricelist_factory
    ):
        """Test filtering by code."""
        pricelist = await pricelist_factory(name="Standard Price")
        await pricelist_factory(name="Premium Price")

        response = await async_client.get(
            f"/api/v1/pricelists/?code={pricelist.code}"
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["code"] == pricelist.code

    async def test_get_pricelists_filter_by_is_active(
        self, async_client: AsyncClient, pricelist_factory
    ):
        """Test filtering by is_active status."""
        await pricelist_factory(name="Active Pricelist", is_active=True)
        await pricelist_factory(name="Inactive Pricelist", is_active=False)

        # Test active filter
        response = await async_client.get("/api/v1/pricelists/?is_active=true")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is True

        # Test inactive filter
        response = await async_client.get("/api/v1/pricelists/?is_active=false")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is False

    async def test_get_pricelists_combined_filters(
        self, async_client: AsyncClient, pricelist_factory
    ):
        """Test combining multiple filters."""
        pricelist = await pricelist_factory(
            name="Standard Price", is_active=True
        )
        await pricelist_factory(name="Premium Price", is_active=False)

        response = await async_client.get(
            f"/api/v1/pricelists/?code={pricelist.code}&is_active=true"
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["code"] == pricelist.code
        assert data[0]["is_active"] is True


class TestCreatePricelist:
    """Test cases for POST /pricelists/ endpoint."""

    async def test_create_pricelist_success(self, async_client: AsyncClient):
        """Test creating pricelist successfully."""
        pricelist_data = {"name": "Standard Price", "description": "Standard pricing"}

        response = await async_client.post(
            "/api/v1/pricelists/", json=pricelist_data
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Standard Price"
        assert data["description"] == "Standard pricing"
        assert data["code"] == "STANDARD-PRICE"

    async def test_create_pricelist_duplicate_name(
        self, async_client: AsyncClient, pricelist_factory
    ):
        """Test creating pricelist with duplicate name."""
        await pricelist_factory(name="Standard Price")

        pricelist_data = {"name": "Standard Price"}
        response = await async_client.post(
            "/api/v1/pricelists/", json=pricelist_data
        )
        error = response.json()["error"]

        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Pricelist with name 'Standard Price' already exists"
        )
        assert error["details"] is None


class TestGetPricelist:
    """Test cases for GET /pricelists/{id} endpoint."""

    async def test_get_pricelist_success(
        self, async_client: AsyncClient, pricelist_factory
    ):
        """Test getting pricelist by ID successfully."""
        pricelist = await pricelist_factory(
            name="Standard Price", description="Standard pricing"
        )

        response = await async_client.get(f"/api/v1/pricelists/{pricelist.id}")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == pricelist.id
        assert data["name"] == "Standard Price"
        assert data["description"] == "Standard pricing"
        assert data["code"] == pricelist.code

    async def test_get_pricelist_not_found(self, async_client: AsyncClient):
        """Test getting non-existent pricelist."""
        response = await async_client.get("/api/v1/pricelists/999")
        error = response.json()["error"]

        assert response.status_code == 404
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Pricelist with id 999 not found"
        assert error["details"] is None


class TestUpdatePricelist:
    """Test cases for PUT /pricelists/{id} endpoint."""

    async def test_update_pricelist_success(
        self, async_client: AsyncClient, pricelist_factory
    ):
        """Test updating pricelist successfully."""
        pricelist = await pricelist_factory(
            name="Standard Price", description="Standard pricing"
        )
        assert pricelist.name == "Standard Price"
        assert pricelist.description == "Standard pricing"

        update_data = {
            "name": "Updated Standard Price",
            "description": "Updated standard pricing"
        }
        response = await async_client.put(
            f"/api/v1/pricelists/{pricelist.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == pricelist.id
        assert data["name"] == "Updated Standard Price"
        assert data["description"] == "Updated standard pricing"

    async def test_update_pricelist_not_found(self, async_client: AsyncClient):
        """Test updating non-existent pricelist."""
        update_data = {"name": "Updated Name"}
        response = await async_client.put(
            "/api/v1/pricelists/999", json=update_data
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Pricelist with id 999 not found"
        assert error["details"] is None

    async def test_update_pricelist_duplicate_name(
        self, async_client: AsyncClient, pricelist_factory
    ):
        """Test updating pricelist with duplicate name."""
        await pricelist_factory(name="Standard Price")
        pricelist2 = await pricelist_factory(name="Premium Price")

        update_data = {"name": "Standard Price"}
        response = await async_client.put(
            f"/api/v1/pricelists/{pricelist2.id}", json=update_data
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Pricelist with name 'Standard Price' already exists"
        )
        assert error["details"] is None


class TestDeletePricelist:
    """Test cases for DELETE /pricelists/{id} endpoint."""

    async def test_delete_pricelist_success(
        self, async_client: AsyncClient, pricelist_factory
    ):
        """Test deleting pricelist successfully."""
        pricelist = await pricelist_factory(name="Standard Price")

        response = await async_client.delete(
            f"/api/v1/pricelists/{pricelist.id}"
        )

        assert response.status_code == 204

    async def test_delete_pricelist_not_found(self, async_client: AsyncClient):
        """Test deleting non-existent pricelist."""
        response = await async_client.delete("/api/v1/pricelists/999")

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Pricelist with id 999 not found"
        assert error["details"] is None

    async def test_delete_pricelist_with_price_details(
        self, async_client: AsyncClient, pricelist_factory, price_detail_factory
    ):
        """Test deleting pricelist that has associated price details."""
        pricelist = await pricelist_factory(name="Standard Price")

        # Create a price detail under this pricelist
        await price_detail_factory(
            price=100.00,
            pricelist=pricelist
        )

        response = await async_client.delete(
            f"/api/v1/pricelists/{pricelist.id}"
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Cannot delete pricelist. "
            "It has 1 associated price details"
        )
        assert error["details"] is None


class TestPricelistEndpointIntegration:
    """Integration tests for pricelist endpoints."""

    async def test_full_crud_workflow(
        self, async_client: AsyncClient
    ):
        """Test complete CRUD workflow for pricelists."""
        # Create
        create_data = {
            "name": "Standard Price",
            "description": "Standard pricing for all products"
        }
        response = await async_client.post("/api/v1/pricelists/", json=create_data)
        assert response.status_code == 201
        created_data = response.json()["data"]
        pricelist_id = created_data["id"]

        # Read individual
        response = await async_client.get(f"/api/v1/pricelists/{pricelist_id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Standard Price"
        assert data["description"] == "Standard pricing for all products"

        # Read list
        response = await async_client.get("/api/v1/pricelists/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "Standard Price"
        assert data[0]["description"] == "Standard pricing for all products"

        # Update
        update_data = {
            "name": "Updated Standard Price",
            "description": "Updated pricing",
            "is_active": False
        }
        response = await async_client.put(
            f"/api/v1/pricelists/{pricelist_id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Updated Standard Price"
        assert data["description"] == "Updated pricing"
        assert data['is_active'] is False

        # Delete
        response = await async_client.delete(
            f"/api/v1/pricelists/{pricelist_id}"
        )
        assert response.status_code == 204

        # Verify item is deleted
        response = await async_client.get(f"/api/v1/pricelists/{pricelist_id}")
        assert response.status_code == 404
        error = response.json()["error"]
        assert error["message"] == f"Pricelist with id {pricelist_id} not found"

    async def test_pricelist_with_price_details_workflow(
        self, async_client: AsyncClient, price_detail_factory
    ):
        """Test pricelist workflow with associated price details."""
        # Create pricelist
        create_data = {"name": "Standard Price", "description": "Standard pricing"}
        response = await async_client.post("/api/v1/pricelists/", json=create_data)
        assert response.status_code == 201
        pricelist_id = response.json()["data"]["id"]

        # Create price details using factory (simulating external creation)
        await price_detail_factory(
            price=100.00, pricelist_id=pricelist_id, minimum_quantity=1
        )
        await price_detail_factory(
            price=200.00, pricelist_id=pricelist_id, minimum_quantity=2
        )

        # Try to delete pricelist (should fail)
        response = await async_client.delete(
            f"/api/v1/pricelists/{pricelist_id}"
        )
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["message"] == (
            "Cannot delete pricelist. "
            "It has 2 associated price details"
        )
