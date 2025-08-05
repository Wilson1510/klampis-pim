from httpx import AsyncClient


class TestConstraintEndpoint:
    """Test cases for constraint validation on create endpoints."""

    async def test_create_model_with_special_character_string(
        self, async_client: AsyncClient
    ):
        """Test creating supplier with special characters in name field."""
        # Test with special characters that should be allowed
        supplier_data = {
            "name": "PT. Maju & Berkah - Indonesia (2024)",
            "company_type": "PT",
            "address": "Jl. Kebon Jeruk No. 123",
            "contact": "081234567890",
            "email": "maju.berkah@test.com"
        }

        response = await async_client.post("/api/v1/suppliers/", json=supplier_data)

        assert response.status_code == 422
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "HTTP_ERROR_422",
                "message": (
                    "Column 'name' can only contain alphabet letters, numbers, "
                    "underscores, and spaces."
                ),
                "details": None
            }
        }

    async def test_create_model_empty_string_field(
        self, async_client: AsyncClient
    ):
        """Test creating product with empty string in required name field."""
        product_data = {
            "name": "",  # Empty string should fail min_length=1
            "description": "Test product description",
            "category_id": 1,
            "supplier_id": 1
        }

        response = await async_client.post("/api/v1/products/", json=product_data)

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
                        "msg": "String should have at least 1 character",
                        "type": "string_too_short"
                    }
                ]
            }
        }

    async def test_create_model_string_length_exceeded(
        self, async_client: AsyncClient
    ):
        """Test creating attribute with name exceeding max_length constraint."""
        # Attribute name has max_length=50
        long_name = "A" * 51  # 51 characters, exceeds max_length=50

        attribute_data = {
            "name": long_name,
            "data_type": "TEXT",
            "uom": "pieces"
        }

        response = await async_client.post("/api/v1/attributes/", json=attribute_data)

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
                        "msg": "String should have at most 50 characters",
                        "type": "string_too_long"
                    }
                ]
            }
        }

    async def test_create_model_number_limit_subceeded(
        self,
        async_client: AsyncClient,
        product_factory,
        pricelist_factory
    ):
        """Test creating SKU with price that subceeds minimum positive decimal."""
        # Create required dependencies
        product = await product_factory()
        pricelist = await pricelist_factory(name="Test Pricelist")

        # PositiveDecimal requires gt=0, so 0 or negative should fail
        sku_data = {
            "name": "Test SKU",
            "description": "Test SKU description",
            "product_id": product.id,
            "price_details": [
                {
                    "pricelist_id": pricelist.id,
                    "price": 0,  # Should fail PositiveDecimal constraint (gt=0)
                    "minimum_quantity": 1
                }
            ],
            "attribute_values": []
        }

        response = await async_client.post("/api/v1/skus/", json=sku_data)

        assert response.status_code == 422
        assert response.json() == {
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": [
                    {
                        "loc": ["body", "price_details", 0, "price"],
                        "msg": "Input should be greater than 0",
                        "type": "greater_than"
                    }
                ]
            }
        }
