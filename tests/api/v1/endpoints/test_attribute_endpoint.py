from httpx import AsyncClient


class TestGetAttributes:
    """Test cases for GET /attributes/ endpoint."""

    async def test_get_attributes_success(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test getting attributes successfully."""
        # Create test data
        await attribute_factory(name="Color", data_type="TEXT")
        await attribute_factory(name="Weight", data_type="NUMBER")

        response = await async_client.get("/api/v1/attributes/")

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
        names = {item["name"] for item in data}
        expected_names = {"Color", "Weight"}
        assert names == expected_names

        for item in data:
            assert "name" in item
            assert "code" in item
            assert "data_type" in item
            assert "uom" in item

    async def test_get_attributes_filter_by_name(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test filtering by name."""
        await attribute_factory(name="Color and Shade")
        await attribute_factory(name="Weight and Size")

        response = await async_client.get("/api/v1/attributes/?name=Color")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "Color and Shade"

    async def test_get_attributes_filter_by_code(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test filtering by code."""
        attribute = await attribute_factory(name="Color")
        await attribute_factory(name="Weight")

        response = await async_client.get(
            f"/api/v1/attributes/?code={attribute.code}"
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["code"] == attribute.code

    async def test_get_attributes_filter_by_data_type(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test filtering by data_type."""
        await attribute_factory(name="Color", data_type="TEXT")
        await attribute_factory(name="Weight", data_type="NUMBER")

        response = await async_client.get("/api/v1/attributes/?data_type=TEXT")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["data_type"] == "TEXT"

    async def test_get_attributes_filter_by_is_active(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test filtering by is_active status."""
        await attribute_factory(name="Active Attribute", is_active=True)
        await attribute_factory(name="Inactive Attribute", is_active=False)

        # Test active filter
        response = await async_client.get("/api/v1/attributes/?is_active=true")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is True

        # Test inactive filter
        response = await async_client.get("/api/v1/attributes/?is_active=false")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is False

    async def test_get_attributes_combined_filters(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test combining multiple filters."""
        attribute = await attribute_factory(
            name="Color", data_type="TEXT", is_active=True
        )
        await attribute_factory(name="Weight", data_type="NUMBER", is_active=False)

        response = await async_client.get(
            f"/api/v1/attributes/?code={attribute.code}&is_active=true"
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["code"] == attribute.code
        assert data[0]["is_active"] is True


class TestCreateAttribute:
    """Test cases for POST /attributes/ endpoint."""

    async def test_create_attribute_success(self, async_client: AsyncClient):
        """Test creating attribute successfully."""
        attribute_data = {"name": "Color", "data_type": "TEXT"}

        response = await async_client.post(
            "/api/v1/attributes/", json=attribute_data
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Color"
        assert data["data_type"] == "TEXT"
        assert data["code"] == "COLOR"

    async def test_create_attribute_with_uom(self, async_client: AsyncClient):
        """Test creating attribute with unit of measure."""
        attribute_data = {
            "name": "Weight",
            "data_type": "NUMBER",
            "uom": "kg"
        }

        response = await async_client.post(
            "/api/v1/attributes/", json=attribute_data
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Weight"
        assert data["data_type"] == "NUMBER"
        assert data["uom"] == "kg"

    async def test_create_attribute_duplicate_name(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test creating attribute with duplicate name."""
        await attribute_factory(name="Color")

        attribute_data = {"name": "Color"}
        response = await async_client.post(
            "/api/v1/attributes/", json=attribute_data
        )
        error = response.json()["error"]

        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Attribute with name 'Color' already exists"
        )
        assert error["details"] is None


class TestGetAttribute:
    """Test cases for GET /attributes/{id} endpoint."""

    async def test_get_attribute_success(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test getting attribute by ID successfully."""
        attribute = await attribute_factory(name="Color", data_type="TEXT")

        response = await async_client.get(f"/api/v1/attributes/{attribute.id}")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == attribute.id
        assert data["name"] == "Color"
        assert data["data_type"] == "TEXT"
        assert data["code"] == attribute.code

    async def test_get_attribute_not_found(self, async_client: AsyncClient):
        """Test getting non-existent attribute."""
        response = await async_client.get("/api/v1/attributes/999")
        error = response.json()["error"]

        assert response.status_code == 404
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Attribute with id 999 not found"
        assert error["details"] is None


class TestUpdateAttribute:
    """Test cases for PUT /attributes/{id} endpoint."""

    async def test_update_attribute_success(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test updating attribute successfully."""
        attribute = await attribute_factory(name="Color", data_type="TEXT")
        assert attribute.name == "Color"
        assert attribute.data_type == "TEXT"

        update_data = {"name": "Product Color", "data_type": "TEXT", "uom": "unit"}
        response = await async_client.put(
            f"/api/v1/attributes/{attribute.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == attribute.id
        assert data["name"] == "Product Color"
        assert data["data_type"] == "TEXT"
        assert data["uom"] == "unit"

    async def test_update_attribute_not_found(self, async_client: AsyncClient):
        """Test updating non-existent attribute."""
        update_data = {"name": "Updated Name"}
        response = await async_client.put(
            "/api/v1/attributes/999", json=update_data
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Attribute with id 999 not found"
        assert error["details"] is None

    async def test_update_attribute_duplicate_name(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test updating attribute with duplicate name."""
        await attribute_factory(name="Color")
        attribute2 = await attribute_factory(name="Weight")

        update_data = {"name": "Color"}
        response = await async_client.put(
            f"/api/v1/attributes/{attribute2.id}", json=update_data
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Attribute with name 'Color' already exists"
        )
        assert error["details"] is None


class TestDeleteAttribute:
    """Test cases for DELETE /attributes/{id} endpoint."""

    async def test_delete_attribute_success(
        self, async_client: AsyncClient, attribute_factory
    ):
        """Test deleting attribute successfully."""
        attribute = await attribute_factory(name="Color")

        response = await async_client.delete(
            f"/api/v1/attributes/{attribute.id}"
        )

        assert response.status_code == 204

    async def test_delete_attribute_not_found(self, async_client: AsyncClient):
        """Test deleting non-existent attribute."""
        response = await async_client.delete("/api/v1/attributes/999")

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Attribute with id 999 not found"
        assert error["details"] is None

    async def test_delete_attribute_with_sku_values(
        self, async_client: AsyncClient, attribute_factory, sku_attribute_value_factory
    ):
        """Test deleting attribute that has associated SKU attribute values."""
        attribute = await attribute_factory(name="Color")

        # Create a SKU attribute value under this attribute
        await sku_attribute_value_factory(
            value="Red",
            attribute=attribute
        )

        response = await async_client.delete(
            f"/api/v1/attributes/{attribute.id}"
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Cannot delete attribute. "
            "It has 1 associated SKU attribute values"
        )
        assert error["details"] is None


class TestAttributeEndpointIntegration:
    """Integration tests for attribute endpoints."""

    async def test_full_crud_workflow(
        self, async_client: AsyncClient
    ):
        """Test complete CRUD workflow for attributes."""
        # Create
        create_data = {"name": "Color", "data_type": "TEXT", "uom": "unit"}
        response = await async_client.post("/api/v1/attributes/", json=create_data)
        assert response.status_code == 201
        created_data = response.json()["data"]
        attribute_id = created_data["id"]

        # Read individual
        response = await async_client.get(f"/api/v1/attributes/{attribute_id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Color"
        assert data["data_type"] == "TEXT"
        assert data["uom"] == "unit"

        # Read list
        response = await async_client.get("/api/v1/attributes/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "Color"
        assert data[0]["data_type"] == "TEXT"
        assert data[0]["uom"] == "unit"

        # Update
        update_data = {"name": "Product Color", "data_type": "TEXT", "is_active": False}
        response = await async_client.put(
            f"/api/v1/attributes/{attribute_id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Product Color"
        assert data["data_type"] == "TEXT"
        assert data['is_active'] is False

        # Delete
        response = await async_client.delete(
            f"/api/v1/attributes/{attribute_id}"
        )
        assert response.status_code == 204

        # Verify item is deleted
        response = await async_client.get(f"/api/v1/attributes/{attribute_id}")
        assert response.status_code == 404
        error = response.json()["error"]
        assert error["message"] == f"Attribute with id {attribute_id} not found"

    async def test_attribute_with_sku_values_workflow(
        self, async_client: AsyncClient, sku_attribute_value_factory
    ):
        """Test attribute workflow with associated SKU attribute values."""
        # Create attribute
        create_data = {"name": "Color", "data_type": "TEXT"}
        response = await async_client.post("/api/v1/attributes/", json=create_data)
        assert response.status_code == 201
        attribute_id = response.json()["data"]["id"]

        # Create SKU attribute values using factory (simulating external creation)
        await sku_attribute_value_factory(
            value="Red", attribute_id=attribute_id
        )

        # Try to delete attribute (should fail)
        response = await async_client.delete(
            f"/api/v1/attributes/{attribute_id}"
        )
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["message"] == (
            "Cannot delete attribute. "
            "It has 1 associated SKU attribute values"
        )
