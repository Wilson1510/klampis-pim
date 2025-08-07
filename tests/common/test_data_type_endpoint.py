from httpx import AsyncClient


class TestDataTypeEndpoint:
    """Test cases for data type validation on endpoints."""

    async def test_get_models_pagination_parameters_not_integer(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test GET request with non-integer pagination parameters."""
        # Test skip parameter with string value
        response = await async_client.get(
            "/api/v1/products/?skip=not_a_number&limit=10",
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
                        "loc": ["query", "skip"],
                        "msg": (
                            "Input should be a valid integer, unable to parse string"
                            " as an integer"
                        ),
                        "type": "int_parsing"
                    }
                ]
            }
        }

    async def test_get_models_filter_parameter_data_type_not_match(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test GET request with filter parameter having wrong data type."""
        # Test category_id parameter with string value instead of int
        response = await async_client.get(
            "/api/v1/products/?category_id=not_a_number",
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
                        "loc": ["query", "category_id"],
                        "msg": (
                            "Input should be a valid integer, unable to parse string"
                            " as an integer"
                        ),
                        "type": "int_parsing"
                    }
                ]
            }
        }

    async def test_create_model_string_field_not_string(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating attribute with non-string value in name field."""
        # name field expects StrictStr, providing integer should fail
        attribute_data = {
            "name": 12345,  # Integer instead of string
            "data_type": "TEXT",
            "uom": "pieces"
        }

        response = await async_client.post(
            "/api/v1/attributes/",
            json=attribute_data,
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
                        "msg": "Input should be a valid string",
                        "type": "string_type"
                    }
                ]
            }
        }

    async def test_create_model_integer_field_not_integer(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating product with non-integer value in category_id field."""
        # category_id field expects StrictPositiveInt, providing string should fail
        product_data = {
            "name": "Test Product",
            "description": "Test description",
            "category_id": "not_a_number",  # String instead of integer
            "supplier_id": 1
        }

        response = await async_client.post(
            "/api/v1/products/",
            json=product_data,
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
                        "loc": ["body", "category_id"],
                        "msg": (
                            "Input should be a valid integer"
                        ),
                        "type": "int_type"
                    }
                ]
            }
        }

    async def test_create_model_boolean_field_not_boolean(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating supplier with non-boolean value in is_active field."""
        # is_active field expects StrictBool, providing string should fail
        supplier_data = {
            "name": "Test Supplier",
            "company_type": "PT",
            "address": "Test Address",
            "contact": "081234567890",
            "email": "test@supplier.com",
            "is_active": "not_a_boolean"  # String instead of boolean
        }

        response = await async_client.post(
            "/api/v1/suppliers/",
            json=supplier_data,
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
                        "loc": ["body", "is_active"],
                        "msg": "Input should be a valid boolean",
                        "type": "bool_type"
                    }
                ]
            }
        }

    async def test_create_model_literal_field_not_match(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test creating attribute with invalid literal value in data_type field."""
        # data_type field expects Literal["TEXT", "NUMBER", "BOOLEAN", "DATE"]
        attribute_data = {
            "name": "Test Attribute",
            "data_type": "INVALID_TYPE",  # Invalid literal value
            "uom": "pieces"
        }

        response = await async_client.post(
            "/api/v1/attributes/",
            json=attribute_data,
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
                        "loc": ["body", "data_type"],
                        "msg": (
                            "Input should be 'TEXT', 'NUMBER', 'BOOLEAN' or 'DATE'"
                        ),
                        "type": "literal_error"
                    }
                ]
            }
        }

    async def test_create_model_list_field_not_list(
        self, async_client: AsyncClient, product_factory, auth_headers_system
    ):
        """Test creating SKU with non-list value in price_details field."""
        # Create required dependencies
        product = await product_factory()

        # price_details field expects List[PriceDetailCreate]
        sku_data = {
            "name": "Test SKU",
            "description": "Test SKU description",
            "product_id": product.id,
            "price_details": "not_a_list",  # String instead of list
            "attribute_values": []
        }

        response = await async_client.post(
            "/api/v1/skus/",
            json=sku_data,
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
                        "loc": ["body", "price_details"],
                        "msg": "Input should be a valid list",
                        "type": "list_type"
                    }
                ]
            }
        }

    async def test_get_model_id_not_integer(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test GET request for single model with non-integer ID."""
        # Test getting a product with non-integer ID
        response = await async_client.get(
            "/api/v1/products/not_a_number",
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
                        "loc": ["path", "product_id"],
                        "msg": (
                            "Input should be a valid integer, unable to parse string"
                            " as an integer"
                        ),
                        "type": "int_parsing"
                    }
                ]
            }
        }

    async def test_delete_model_id_not_integer(
        self, async_client: AsyncClient, auth_headers_system
    ):
        """Test DELETE request with non-integer ID."""
        # Test deleting a supplier with non-integer ID
        response = await async_client.delete(
            "/api/v1/suppliers/not_a_number",
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
                        "loc": ["path", "supplier_id"],
                        "msg": (
                            "Input should be a valid integer, unable to parse string"
                            " as an integer"
                        ),
                        "type": "int_parsing"
                    }
                ]
            }
        }
