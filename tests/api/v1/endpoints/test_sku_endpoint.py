from httpx import AsyncClient


class TestGetSkus:
    """Test cases for GET /skus/ endpoint."""

    async def test_get_skus_success(
        self, async_client: AsyncClient, sku_factory, price_detail_factory,
        attribute_factory, sku_attribute_value_factory, auth_headers_system
    ):
        """Test getting SKUs successfully."""
        # Create test data
        sku1 = await sku_factory(name="SKU 1")
        sku2 = await sku_factory(name="SKU 2")

        attribute1 = await attribute_factory(name="Attribute 1", data_type="TEXT")
        attribute2 = await attribute_factory(name="Attribute 2", data_type="TEXT")

        await price_detail_factory(sku=sku1, price=100, minimum_quantity=1)
        await price_detail_factory(sku=sku1, price=200, minimum_quantity=2)
        await price_detail_factory(sku=sku2, price=300, minimum_quantity=3)
        await price_detail_factory(sku=sku2, price=400, minimum_quantity=4)

        await sku_attribute_value_factory(
            sku=sku1, attribute=attribute1, value="Value 1"
        )
        await sku_attribute_value_factory(
            sku=sku1, attribute=attribute2, value="Value 2"
        )
        await sku_attribute_value_factory(
            sku=sku2, attribute=attribute1, value="Value 3"
        )
        await sku_attribute_value_factory(
            sku=sku2, attribute=attribute2, value="Value 4"
        )

        response = await async_client.get(
            "/api/v1/skus/", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
        names = {item["name"] for item in data}
        expected_names = {"SKU 1", "SKU 2"}
        assert names == expected_names

        price_details = [item["price_details"] for item in data]
        pd_sku1 = {pd["price"] for pd in price_details[0]}
        pd_sku2 = {pd["price"] for pd in price_details[1]}
        assert pd_sku1 == {'100.00', '200.00'}
        assert pd_sku2 == {'300.00', '400.00'}

        attr_value_sku1 = {av["value"] for av in data[0]["sku_attribute_values"]}
        attr_value_sku2 = {av["value"] for av in data[1]["sku_attribute_values"]}
        assert attr_value_sku1 == {'Value 1', 'Value 2'}
        assert attr_value_sku2 == {'Value 3', 'Value 4'}

        for item in data:
            assert "name" in item
            assert "slug" in item
            assert "sku_number" in item
            assert "description" in item
            assert "product_id" in item
            assert "full_path" in item
            assert "price_details" in item
            assert "sku_attribute_values" in item

    async def test_get_skus_filter_by_name(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test filtering by name."""
        await sku_factory(name="iPhone 15 Pro Max")
        await sku_factory(name="Samsung Galaxy S24")

        response = await async_client.get(
            "/api/v1/skus/?name=iPhone", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "iPhone 15 Pro Max"

    async def test_get_skus_filter_by_slug(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test filtering by slug."""
        sku = await sku_factory(name="iPhone 15 Pro")
        await sku_factory(name="Samsung Galaxy S24")

        response = await async_client.get(
            f"/api/v1/skus/?slug={sku.slug}", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["slug"] == sku.slug

    async def test_get_skus_filter_by_sku_number(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test filtering by SKU number."""
        sku = await sku_factory(name="iPhone 15 Pro")
        await sku_factory(name="Samsung Galaxy S24")

        response = await async_client.get(
            f"/api/v1/skus/?sku_number={sku.sku_number}", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["sku_number"] == sku.sku_number

    async def test_get_skus_filter_by_product_id(
        self, async_client: AsyncClient, sku_factory, product_factory,
        auth_headers_system
    ):
        """Test filtering by product ID."""
        product1 = await product_factory(name="iPhone 15")
        product2 = await product_factory(name="Samsung Galaxy S24")

        await sku_factory(name="iPhone 15 Pro", product=product1)
        await sku_factory(name="Samsung Galaxy S24 Ultra", product=product2)

        response = await async_client.get(
            f"/api/v1/skus/?product_id={product1.id}", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["product_id"] == product1.id

    async def test_get_skus_filter_by_is_active(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test filtering by is_active status."""
        await sku_factory(name="Active SKU", is_active=True)
        await sku_factory(name="Inactive SKU", is_active=False)

        # Test active filter
        response = await async_client.get(
            "/api/v1/skus/?is_active=true", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is True

        # Test inactive filter
        response = await async_client.get(
            "/api/v1/skus/?is_active=false", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["is_active"] is False

    async def test_get_skus_combined_filters(
        self, async_client: AsyncClient, sku_factory, product_factory,
        auth_headers_system
    ):
        """Test combining multiple filters."""
        product = await product_factory(name="iPhone 15")
        await sku_factory(
            name="iPhone 15 Pro",
            product=product,
            is_active=True
        )
        await sku_factory(
            name="Samsung Galaxy S24",
            is_active=False
        )

        response = await async_client.get(
            f"/api/v1/skus/?product_id={product.id}&is_active=true",
            headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["product_id"] == product.id
        assert data[0]["is_active"] is True

    async def test_get_skus_by_user(
        self, async_client: AsyncClient, sku_factory, price_detail_factory,
        attribute_factory, sku_attribute_value_factory, auth_headers_user
    ):
        """Test getting SKUs by user."""
        # Create test data
        sku1 = await sku_factory(name="SKU 1")
        sku2 = await sku_factory(name="SKU 2")

        attribute1 = await attribute_factory(name="Attribute 1", data_type="TEXT")
        attribute2 = await attribute_factory(name="Attribute 2", data_type="TEXT")

        await price_detail_factory(sku=sku1, price=100, minimum_quantity=1)
        await price_detail_factory(sku=sku2, price=300, minimum_quantity=3)

        await sku_attribute_value_factory(
            sku=sku1, attribute=attribute1, value="Value 1"
        )
        await sku_attribute_value_factory(
            sku=sku2, attribute=attribute2, value="Value 2"
        )

        response = await async_client.get(
            "/api/v1/skus/", headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        # Verify response structure and data
        names = {item["name"] for item in data}
        expected_names = {"SKU 1", "SKU 2"}
        assert names == expected_names

        for item in data:
            assert "name" in item
            assert "slug" in item
            assert "sku_number" in item
            assert "description" in item
            assert "product_id" in item

    async def test_get_skus_unauthenticated(
        self, async_client: AsyncClient
    ):
        """Test getting SKUs without authentication."""
        response = await async_client.get("/api/v1/skus/")
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestCreateSku:
    """Test cases for POST /skus/ endpoint."""

    async def test_create_sku_success(
        self, async_client: AsyncClient, product_factory, pricelist_factory,
        attribute_factory, auth_headers_system
    ):
        """Test creating SKU successfully."""
        product = await product_factory(name="iPhone 15")
        pricelist = await pricelist_factory(name="Retail")
        attribute = await attribute_factory(name="Color", data_type="TEXT")

        sku_data = {
            "name": "iPhone 15 Pro Max",
            "description": "Latest iPhone model",
            "product_id": product.id,
            "price_details": [
                {
                    "pricelist_id": pricelist.id,
                    "price": 1299.99,
                    "minimum_quantity": 1
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "Space Black"
                }
            ]
        }

        response = await async_client.post(
            "/api/v1/skus/", json=sku_data, headers=auth_headers_system
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "iPhone 15 Pro Max"
        assert data["description"] == "Latest iPhone model"
        assert data["product_id"] == product.id
        assert data["slug"] == "iphone-15-pro-max"
        assert len(data["full_path"]) == 3
        assert len(data["sku_number"]) == 10  # Auto-generated 10-char hex
        assert len(data["price_details"]) == 1
        assert len(data["sku_attribute_values"]) == 1
        assert data["full_path"][0]["type"] == "Category"
        assert data["full_path"][0]["name"] == "Test Category"
        assert data["full_path"][1]["type"] == "Product"
        assert data["full_path"][1]["name"] == "iPhone 15"
        assert data["full_path"][2]["type"] == "SKU"
        assert data["full_path"][2]["name"] == "iPhone 15 Pro Max"
        assert data["price_details"][0]["price"] == '1299.99'
        assert data["price_details"][0]["minimum_quantity"] == 1
        assert data["price_details"][0]["pricelist"]["id"] == pricelist.id
        assert data["price_details"][0]["pricelist"]["name"] == "Retail"
        assert data["price_details"][0]["pricelist"]["code"] == "RETAIL"
        assert data["sku_attribute_values"][0]["value"] == "Space Black"
        assert data["sku_attribute_values"][0]["attribute"]["id"] == attribute.id
        assert data["sku_attribute_values"][0]["attribute"]["name"] == "Color"
        assert data["sku_attribute_values"][0]["attribute"]["data_type"] == "TEXT"
        assert data["sku_attribute_values"][0]["attribute"]["uom"] is None

    async def test_create_sku_duplicate_name(
        self, async_client: AsyncClient, sku_factory, product_factory,
        pricelist_factory, attribute_factory, auth_headers_system
    ):
        """Test creating SKU with duplicate name."""
        product = await product_factory(name="iPhone 15")
        await sku_factory(name="iPhone 15 Pro", product=product)

        pricelist = await pricelist_factory(name="Retail")
        attribute = await attribute_factory(name="Color", data_type="TEXT")

        sku_data = {
            "name": "iPhone 15 Pro",
            "product_id": product.id,
            "price_details": [
                {
                    "pricelist_id": pricelist.id,
                    "price": 999.99,
                    "minimum_quantity": 1
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "Blue"
                }
            ]
        }

        response = await async_client.post(
            "/api/v1/skus/", json=sku_data, headers=auth_headers_system
        )
        error = response.json()["error"]

        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == "SKU with name 'iPhone 15 Pro' already exists"
        assert error["details"] is None

    async def test_create_sku_nonexistent_attribute(
        self, async_client: AsyncClient, product_factory, pricelist_factory,
        auth_headers_system
    ):
        """Test creating SKU with non-existent attribute."""
        product = await product_factory(name="iPhone 15")
        pricelist = await pricelist_factory(name="Retail")

        sku_data = {
            "name": "iPhone 15 Pro",
            "product_id": product.id,
            "price_details": [
                {
                    "pricelist_id": pricelist.id,
                    "price": 999.99,
                    "minimum_quantity": 1
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": 999,
                    "value": "Blue"
                }
            ]
        }

        response = await async_client.post(
            "/api/v1/skus/", json=sku_data, headers=auth_headers_system
        )
        error = response.json()["error"]

        assert response.status_code == 404
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Attributes with IDs {999} not found"
        assert error["details"] is None

    async def test_create_sku_nonexistent_pricelist(
        self, async_client: AsyncClient, product_factory, attribute_factory,
        auth_headers_system
    ):
        """Test creating SKU with non-existent pricelist."""
        product = await product_factory(name="iPhone 15")
        attribute = await attribute_factory(name="Color", data_type="TEXT")

        sku_data = {
            "name": "iPhone 15 Pro",
            "product_id": product.id,
            "price_details": [
                {
                    "pricelist_id": 999,
                    "price": 999.99,
                    "minimum_quantity": 1
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "Blue"
                }
            ]
        }

        response = await async_client.post(
            "/api/v1/skus/", json=sku_data, headers=auth_headers_system
        )
        error = response.json()["error"]

        assert response.status_code == 404
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "Pricelists with IDs {999} not found"
        assert error["details"] is None

    async def test_create_sku_invalid_attribute_value(
        self, async_client: AsyncClient, product_factory, pricelist_factory,
        attribute_factory, auth_headers_system
    ):
        """Test creating SKU with invalid attribute value for data type."""
        product = await product_factory(name="iPhone 15")
        pricelist = await pricelist_factory(name="Retail")
        # Create NUMBER attribute but provide text value
        attribute = await attribute_factory(name="Weight", data_type="NUMBER")

        sku_data = {
            "name": "iPhone 15 Pro",
            "product_id": product.id,
            "price_details": [
                {
                    "pricelist_id": pricelist.id,
                    "price": 999.99,
                    "minimum_quantity": 1
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "not a number"
                }
            ]
        }

        response = await async_client.post(
            "/api/v1/skus/", json=sku_data, headers=auth_headers_system
        )
        error = response.json()["error"]

        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "Invalid value 'not a number' for attribute 'Weight' (expected NUMBER)"
        )
        assert error["details"] is None

    async def test_create_sku_empty_price_details(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test creating SKU with empty price details."""
        product = await product_factory(name="iPhone 15")

        sku_data = {
            "name": "iPhone 15 Pro",
            "product_id": product.id,
            "price_details": [],  # Empty price details
            "attribute_values": []
        }

        response = await async_client.post(
            "/api/v1/skus/", json=sku_data, headers=auth_headers_system
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "iPhone 15 Pro"
        assert data["product_id"] == product.id
        assert data["slug"] == "iphone-15-pro"
        assert len(data["sku_number"]) == 10  # Auto-generated 10-char hex
        assert data["price_details"] == []
        assert data["sku_attribute_values"] == []

    async def test_create_sku_by_user(
        self, async_client: AsyncClient, product_factory, pricelist_factory,
        attribute_factory, auth_headers_user
    ):
        """Test creating SKU by user."""
        product = await product_factory(name="iPhone 15")
        pricelist = await pricelist_factory(name="Retail")
        attribute = await attribute_factory(name="Color", data_type="TEXT")

        sku_data = {
            "name": "iPhone 15 Pro Max",
            "description": "Latest iPhone model",
            "product_id": product.id,
            "price_details": [
                {
                    "pricelist_id": pricelist.id,
                    "price": 1299.99,
                    "minimum_quantity": 1
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "Space Black"
                }
            ]
        }

        response = await async_client.post(
            "/api/v1/skus/", json=sku_data, headers=auth_headers_user
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "iPhone 15 Pro Max"
        assert data["description"] == "Latest iPhone model"
        assert data["product_id"] == product.id
        assert data["slug"] == "iphone-15-pro-max"

    async def test_create_sku_unauthenticated(
        self, async_client: AsyncClient
    ):
        """Test creating SKU without authentication."""
        sku_data = {
            "name": "iPhone 15 Pro",
            "product_id": 1,
            "price_details": [],
            "attribute_values": []
        }

        response = await async_client.post(
            "/api/v1/skus/", json=sku_data
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestGetSku:
    """Test cases for GET /skus/{id} endpoint."""

    async def test_get_sku_success(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test getting SKU by ID successfully."""
        sku = await sku_factory(name="iPhone 15 Pro")

        response = await async_client.get(
            f"/api/v1/skus/{sku.id}", headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == sku.id
        assert data["name"] == "iPhone 15 Pro"
        assert data["slug"] == sku.slug
        assert data["sku_number"] == sku.sku_number
        assert len(data["full_path"]) == 3
        assert data["price_details"] == []
        assert data["sku_attribute_values"] == []

    async def test_get_sku_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test getting non-existent SKU."""
        response = await async_client.get(
            "/api/v1/skus/999", headers=auth_headers_system
        )
        error = response.json()["error"]

        assert response.status_code == 404
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "SKU with id 999 not found"
        assert error["details"] is None


class TestUpdateSku:
    """Test cases for PUT /skus/{id} endpoint."""

    async def test_update_sku_success(
        self, async_client: AsyncClient, sku_factory, product_factory,
        pricelist_factory, attribute_factory, sku_attribute_value_factory,
        price_detail_factory, auth_headers_system
    ):
        """Test updating SKU basic fields successfully."""
        product = await product_factory(name="iPhone 15")
        pricelist = await pricelist_factory(name="Retail")
        attribute = await attribute_factory(name="Color", data_type="TEXT")
        sku = await sku_factory(name="iPhone 15 Pro", product=product)
        price_detail = await price_detail_factory(
            sku=sku, pricelist=pricelist, price=1299.99, minimum_quantity=1
        )
        price_detail2 = await price_detail_factory(
            sku=sku, pricelist=pricelist, price=4000, minimum_quantity=4
        )
        await sku_attribute_value_factory(
            sku=sku, attribute=attribute, value="Space Black"
        )

        update_data = {
            "name": "iPhone 15 Pro Max",
            "description": "Latest iPhone model",
            "product_id": product.id,
            "price_details_to_create": [
                {
                    "pricelist_id": pricelist.id,
                    "price": 2500,
                    "minimum_quantity": 3
                }
            ],
            "price_details_to_update": [
                {
                    "id": price_detail.id,
                    "price": 1600,
                    "minimum_quantity": 2
                }
            ],
            "price_details_to_delete": [price_detail2.id],
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "Black"
                }
            ]
        }

        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data, headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == sku.id
        assert data["name"] == "iPhone 15 Pro Max"
        assert data["description"] == "Latest iPhone model"
        assert data["slug"] == "iphone-15-pro-max"
        assert data["sku_number"] == sku.sku_number
        assert len(data["full_path"]) == 3
        assert len(data["price_details"]) == 2
        assert data["price_details"][0]["price"] == '2500.00'
        assert data["price_details"][0]["minimum_quantity"] == 3
        assert data["price_details"][0]["pricelist"]["name"] == "Retail"

        assert data["price_details"][1]["price"] == '1600.00'
        assert data["price_details"][1]["minimum_quantity"] == 2
        assert data["price_details"][1]["pricelist"]["name"] == "Retail"

        assert data["sku_attribute_values"][0]["value"] == "Black"
        assert data["sku_attribute_values"][0]["attribute"]["name"] == "Color"
        assert data["sku_attribute_values"][0]["attribute"]["data_type"] == "TEXT"
        assert data["sku_attribute_values"][0]["attribute"]["uom"] is None

    async def test_update_sku_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test updating non-existent SKU."""
        update_data = {"name": "Updated Name"}
        response = await async_client.put(
            "/api/v1/skus/999", json=update_data, headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "SKU with id 999 not found"
        assert error["details"] is None

    async def test_update_sku_duplicate_name(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test updating SKU with duplicate name."""
        await sku_factory(name="iPhone 15 Pro")
        sku2 = await sku_factory(name="iPhone 15 Plus")

        update_data = {"name": "iPhone 15 Pro"}
        response = await async_client.put(
            f"/api/v1/skus/{sku2.id}", json=update_data, headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == "SKU with name 'iPhone 15 Pro' already exists"
        assert error["details"] is None

    async def test_update_sku_delete_all_price_details_fails(
        self, async_client: AsyncClient, sku_factory, price_detail_factory, db_session,
        auth_headers_system
    ):
        """Test that deleting all price details fails."""
        sku = await sku_factory(name="iPhone 15 Pro")
        await price_detail_factory(sku=sku, price=100, minimum_quantity=1)
        await price_detail_factory(sku=sku, price=200, minimum_quantity=2)
        await price_detail_factory(sku=sku, price=300, minimum_quantity=3)

        # Get all price detail IDs
        await db_session.refresh(sku, ['price_details'])
        price_detail_ids = [pd.id for pd in sku.price_details]

        update_data = {
            "price_details_to_delete": price_detail_ids
        }
        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data, headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert "must have at least one active price detail" in error["message"]
        assert error["details"] is None

    async def test_update_sku_delete_price_detail_not_its_own(
        self, async_client: AsyncClient, sku_factory, price_detail_factory,
        auth_headers_system
    ):
        """Test deleting price detail that is not its own."""
        sku = await sku_factory(name="iPhone 15 Pro")
        price_detail = await price_detail_factory(
            sku=sku,
            price=100,
            minimum_quantity=1
        )
        sku2 = await sku_factory(name="iPhone 15 Plus")
        update_data = {
            "price_details_to_delete": [price_detail.id]
        }
        response = await async_client.put(
            f"/api/v1/skus/{sku2.id}", json=update_data, headers=auth_headers_system
        )
        error = response.json()["error"]
        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            f"Price detail with ID {price_detail.id} does not belong to SKU {sku2.id}"
        )
        assert error["details"] is None

    async def test_update_sku_delete_nonexistent_price_detail(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test deleting non-existent price detail."""
        sku = await sku_factory(name="iPhone 15 Pro")

        update_data = {
            "price_details_to_delete": [999]
        }
        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data, headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert "Price detail with ID 999 not found" in error["message"]
        assert error["details"] is None

    async def test_update_sku_create_price_detail_missing_pricelist(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test creating price detail with missing pricelist."""
        sku = await sku_factory(name="iPhone 15 Pro")
        update_data = {
            "price_details_to_create": [
                {
                    "pricelist_id": 999,
                    "price": 100,
                    "minimum_quantity": 1
                }
            ]
        }
        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data, headers=auth_headers_system
        )
        error = response.json()["error"]
        assert response.status_code == 404
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == (
            "Pricelists with IDs {999} not found"
        )
        assert error["details"] is None

    async def test_update_sku_update_attribute_values(
        self, async_client: AsyncClient, sku_factory, attribute_factory,
        sku_attribute_value_factory, auth_headers_system
    ):
        """Test updating attribute values."""
        sku = await sku_factory(name="iPhone 15 Pro")
        attribute = await attribute_factory(name="Color", data_type="TEXT")

        # Add an attribute value
        await sku_attribute_value_factory(
            sku=sku, attribute=attribute, value="Space Black"
        )

        update_data = {
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "Deep Purple"
                }
            ]
        }
        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data, headers=auth_headers_system
        )

        assert response.status_code == 200
        data = response.json()["data"]
        color_attr = next(
            av for av in data["sku_attribute_values"]
            if av["attribute"]["id"] == attribute.id
        )
        assert color_attr["value"] == "Deep Purple"

    async def test_update_sku_invalid_attribute_value(
        self, async_client: AsyncClient, sku_factory, attribute_factory,
        sku_attribute_value_factory, auth_headers_system
    ):
        """Test updating SKU with invalid attribute value."""
        sku = await sku_factory(name="iPhone 15 Pro")
        attribute = await attribute_factory(name="Weight", data_type="NUMBER")
        await sku_attribute_value_factory(sku=sku, attribute=attribute, value="100")

        update_data = {
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "not a number"
                }
            ]
        }
        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data, headers=auth_headers_system
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert "Invalid value 'not a number' for attribute 'Weight'" in error["message"]
        assert error["details"] is None

    async def test_update_sku_nonexistent_attribute(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test updating SKU with non-existent attribute."""
        sku = await sku_factory(name="iPhone 15 Pro")

        update_data = {
            "attribute_values": [
                {
                    "attribute_id": 999,
                    "value": "Blue"
                }
            ]
        }
        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data, headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == (
            "Attribute values with sku id 1 and attribute ids {999} not found"
        )
        assert error["details"] is None

    async def test_update_sku_update_price_detail_not_its_own(
        self, async_client: AsyncClient, sku_factory, price_detail_factory,
        auth_headers_system
    ):
        """Test updating price detail that is not its own."""
        sku = await sku_factory(name="iPhone 15 Pro")
        price_detail = await price_detail_factory(
            sku=sku, price=100, minimum_quantity=1
        )
        sku2 = await sku_factory(name="iPhone 15 Plus")
        update_data = {
            "price_details_to_update": [
                {
                    "id": price_detail.id,
                    "price": 150,
                    "minimum_quantity": 2
                }
            ]
        }
        response = await async_client.put(
            f"/api/v1/skus/{sku2.id}", json=update_data, headers=auth_headers_system
        )
        error = response.json()["error"]
        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            f"Price detail with ID {price_detail.id} does not belong to SKU {sku2.id}"
        )
        assert error["details"] is None

    async def test_update_sku_update_price_detail_not_found(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test updating price detail that is not found."""
        sku = await sku_factory(name="iPhone 15 Pro")
        update_data = {
            "price_details_to_update": [
                {
                    "id": 999,
                    "price": 150,
                    "minimum_quantity": 2
                }
            ]
        }
        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data, headers=auth_headers_system
        )
        error = response.json()["error"]
        assert response.status_code == 404
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == (
            "Price detail with ID 999 not found"
        )
        assert error["details"] is None

    async def test_update_sku_by_user(
        self, async_client: AsyncClient, sku_factory, auth_headers_user
    ):
        """Test updating SKU by user."""
        sku = await sku_factory(name="iPhone 15 Pro")
        update_data = {"name": "iPhone 15 Pro Max"}
        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data, headers=auth_headers_user
        )
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

    async def test_update_sku_unauthenticated(
        self, async_client: AsyncClient, sku_factory
    ):
        """Test updating SKU without authentication."""
        sku = await sku_factory(name="iPhone 15 Pro")
        update_data = {"name": "iPhone 15 Pro Max"}
        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data
        )
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestDeleteSku:
    """Test cases for DELETE /skus/{id} endpoint."""

    async def test_delete_sku_success(
        self, async_client: AsyncClient, sku_factory, auth_headers_system
    ):
        """Test deleting SKU successfully."""
        sku = await sku_factory(name="iPhone 15 Pro")

        response = await async_client.delete(
            f"/api/v1/skus/{sku.id}", headers=auth_headers_system
        )

        assert response.status_code == 204

    async def test_delete_sku_not_found(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test deleting non-existent SKU."""
        response = await async_client.delete(
            "/api/v1/skus/999", headers=auth_headers_system
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "SKU with id 999 not found"
        assert error["details"] is None

    async def test_delete_sku_by_user(
        self, async_client: AsyncClient, sku_factory, auth_headers_user
    ):
        """Test deleting SKU by user."""
        sku = await sku_factory(name="iPhone 15 Pro")
        response = await async_client.delete(
            f"/api/v1/skus/{sku.id}", headers=auth_headers_user
        )
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

    async def test_delete_sku_unauthenticated(
        self, async_client: AsyncClient, sku_factory
    ):
        """Test deleting SKU without authentication."""
        sku = await sku_factory(name="iPhone 15 Pro")
        response = await async_client.delete(f"/api/v1/skus/{sku.id}")
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestSkuEndpointIntegration:
    """Integration tests for SKU endpoints."""

    async def test_full_crud_workflow(
        self, async_client: AsyncClient, product_factory, pricelist_factory,
        attribute_factory, auth_headers_system
    ):
        """Test complete CRUD workflow for SKUs."""
        # Setup dependencies
        product = await product_factory(name="iPhone 15")
        pricelist = await pricelist_factory(name="Retail")
        attribute = await attribute_factory(name="Color", data_type="TEXT")

        # Create
        create_data = {
            "name": "iPhone 15 Pro",
            "description": "Latest iPhone Pro model",
            "product_id": product.id,
            "price_details": [
                {
                    "pricelist_id": pricelist.id,
                    "price": 999.99,
                    "minimum_quantity": 1
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "Space Black"
                }
            ]
        }
        response = await async_client.post(
            "/api/v1/skus/", json=create_data, headers=auth_headers_system
        )
        assert response.status_code == 201
        created_data = response.json()["data"]
        sku_id = created_data["id"]

        # Read individual
        response = await async_client.get(
            f"/api/v1/skus/{sku_id}", headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "iPhone 15 Pro"
        assert data["slug"] == "iphone-15-pro"
        assert data["description"] == "Latest iPhone Pro model"
        assert len(data["price_details"]) == 1
        assert len(data["sku_attribute_values"]) == 1

        # Read list
        response = await async_client.get("/api/v1/skus/", headers=auth_headers_system)
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "iPhone 15 Pro"

        # Update
        update_data = {
            "name": "iPhone 15 Pro Max",
            "description": "Updated description",
            "is_active": False
        }
        response = await async_client.put(
            f"/api/v1/skus/{sku_id}", json=update_data, headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "iPhone 15 Pro Max"
        assert data["slug"] == "iphone-15-pro-max"
        assert data["description"] == "Updated description"
        assert data["is_active"] is False

        # Delete
        response = await async_client.delete(
            f"/api/v1/skus/{sku_id}", headers=auth_headers_system
        )
        assert response.status_code == 204

        # Verify item is deleted
        response = await async_client.get(
            f"/api/v1/skus/{sku_id}", headers=auth_headers_system
        )
        assert response.status_code == 404
        error = response.json()["error"]
        assert error["message"] == f"SKU with id {sku_id} not found"

    async def test_complex_update_workflow(
        self, async_client: AsyncClient, sku_factory, pricelist_factory,
        attribute_factory, price_detail_factory, sku_attribute_value_factory,
        auth_headers_system
    ):
        """Test complex update operations with price details and attributes."""
        # Create SKU with initial data
        sku = await sku_factory(name="iPhone 15 Pro")
        pricelist1 = await pricelist_factory(name="Retail")
        price_detail1 = await price_detail_factory(
            sku=sku,
            price=100,
            minimum_quantity=1,
            is_active=True,
            pricelist_id=pricelist1.id
        )
        pricelist2 = await pricelist_factory(name="Wholesale")
        attribute = await attribute_factory(name="Storage", data_type="TEXT")

        # Add additional price detail and attribute
        price_detail2 = await price_detail_factory(
            sku=sku,
            price=899.99,
            minimum_quantity=10,
            is_active=True,
            pricelist_id=pricelist2.id
        )
        await sku_attribute_value_factory(
            sku=sku,
            attribute=attribute,
            value="128GB"
        )

        # Complex update: create, update, delete price details + update attributes
        pricelist3 = await pricelist_factory(name="VIP")

        update_data = {
            "name": "iPhone 15 Pro Max",
            "price_details_to_create": [
                {
                    "pricelist_id": pricelist3.id,
                    "price": 1199.99,
                    "minimum_quantity": 1
                }
            ],
            "price_details_to_update": [
                {
                    "id": price_detail2.id,
                    "price": 849.99,
                    "minimum_quantity": 5
                }
            ],
            "price_details_to_delete": [price_detail1.id],
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "256GB"
                }
            ]
        }

        response = await async_client.put(
            f"/api/v1/skus/{sku.id}", json=update_data, headers=auth_headers_system
        )
        assert response.status_code == 200
        data = response.json()["data"]

        # Verify updates
        assert data["name"] == "iPhone 15 Pro Max"

        # Check price details
        active_price_ids = [pd["id"] for pd in data["price_details"]]
        assert price_detail1.id not in active_price_ids  # Deleted
        assert price_detail2.id in active_price_ids  # Updated

        # Check updated price
        updated_price = next(
            pd for pd in data["price_details"]
            if pd["id"] == price_detail2.id
        )
        assert updated_price["price"] == '849.99'
        assert updated_price["minimum_quantity"] == 5

        # Check new price detail was created
        vip_prices = [
            pd for pd in data["price_details"]
            if pd["pricelist"]["name"] == "VIP"
        ]
        assert len(vip_prices) == 1
        assert vip_prices[0]["price"] == '1199.99'

        # Check attribute value was updated
        storage_attr = next(
            av for av in data["sku_attribute_values"]
            if av["attribute"]["name"] == "Storage"
        )
        assert storage_attr["value"] == "256GB"

    async def test_full_crud_workflow_by_user(
        self, async_client: AsyncClient, product_factory, pricelist_factory,
        attribute_factory, auth_headers_system, auth_headers_user
    ):
        """Test CRUD workflow with resource ownership by user vs system."""
        # Setup dependencies
        product = await product_factory(name="iPhone 15")
        pricelist = await pricelist_factory(name="Retail")
        attribute = await attribute_factory(name="Color", data_type="TEXT")

        # === CREATE PHASE ===
        # Create SKU by SYSTEM
        system_sku_data = {
            "name": "iPhone 15 Pro System",
            "description": "SKU created by system",
            "product_id": product.id,
            "price_details": [
                {
                    "pricelist_id": pricelist.id,
                    "price": 999.99,
                    "minimum_quantity": 1
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "Space Black"
                }
            ]
        }
        response = await async_client.post(
            "/api/v1/skus/",
            json=system_sku_data,
            headers=auth_headers_system
        )
        assert response.status_code == 201
        system_sku_id = response.json()["data"]["id"]

        # Create SKU by USER
        user_sku_data = {
            "name": "iPhone 15 Pro User",
            "description": "SKU created by user",
            "product_id": product.id,
            "price_details": [
                {
                    "pricelist_id": pricelist.id,
                    "price": 1099.99,
                    "minimum_quantity": 1
                }
            ],
            "attribute_values": [
                {
                    "attribute_id": attribute.id,
                    "value": "Blue"
                }
            ]
        }
        response = await async_client.post(
            "/api/v1/skus/",
            json=user_sku_data,
            headers=auth_headers_user
        )
        assert response.status_code == 201
        user_sku_id = response.json()["data"]["id"]

        # === READ PHASE ===
        # User can read both SKUs (system and their own)
        response = await async_client.get(
            f"/api/v1/skus/{system_sku_id}", headers=auth_headers_user
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "iPhone 15 Pro System"

        response = await async_client.get(
            f"/api/v1/skus/{user_sku_id}", headers=auth_headers_user
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "iPhone 15 Pro User"

        # === UPDATE PHASE ===
        # User tries to update SYSTEM SKU (should fail - ownership check)
        update_data = {"description": "Updated by user"}
        response = await async_client.put(
            f"/api/v1/skus/{system_sku_id}",
            json=update_data,
            headers=auth_headers_user
        )
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

        # User updates their OWN SKU (should succeed)
        update_data = {"description": "Updated by user - own SKU"}
        response = await async_client.put(
            f"/api/v1/skus/{user_sku_id}",
            json=update_data,
            headers=auth_headers_user
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["description"] == "Updated by user - own SKU"

        # System can update both SKUs (admin privileges)
        update_data = {"description": "Updated by system"}
        response = await async_client.put(
            f"/api/v1/skus/{system_sku_id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        assert response.json()["data"]["description"] == "Updated by system"

        response = await async_client.put(
            f"/api/v1/skus/{user_sku_id}",
            json=update_data,
            headers=auth_headers_system
        )
        assert response.status_code == 200
        assert response.json()["data"]["description"] == "Updated by system"

        # === DELETE PHASE ===
        # User tries to delete SYSTEM SKU (should fail - ownership check)
        response = await async_client.delete(
            f"/api/v1/skus/{system_sku_id}", headers=auth_headers_user
        )
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You can only modify your own resources"
        assert error["details"] is None

        # User deletes their OWN SKU (should succeed)
        response = await async_client.delete(
            f"/api/v1/skus/{user_sku_id}", headers=auth_headers_user
        )
        assert response.status_code == 204

        # Verify user's SKU is deleted
        response = await async_client.get(
            f"/api/v1/skus/{user_sku_id}", headers=auth_headers_user
        )
        assert response.status_code == 404

        # System deletes their own SKU (should succeed)
        response = await async_client.delete(
            f"/api/v1/skus/{system_sku_id}", headers=auth_headers_system
        )
        assert response.status_code == 204

        # Verify system SKU is deleted
        response = await async_client.get(
            f"/api/v1/skus/{system_sku_id}", headers=auth_headers_system
        )
        assert response.status_code == 404
