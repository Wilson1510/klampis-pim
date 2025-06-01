# Endpoint Structure
Organize endpoints by resource type, following RESTful conventions:

## **1. Users Endpoints**
```
GET    /api/v1/users/                    # List all users (paginated)
POST   /api/v1/users/                    # Create new user
GET    /api/v1/users/{id}/               # Get user by ID
PUT    /api/v1/users/{id}/               # Update user
DELETE /api/v1/users/{id}/               # Delete user (soft delete)
POST   /api/v1/users/change-password/    # Change user password
```

## **2. Category Types Endpoints**
```
GET    /api/v1/category-types/           # List all category types (paginated)
POST   /api/v1/category-types/           # Create new category type
GET    /api/v1/category-types/{id}/      # Get category type by ID
PUT    /api/v1/category-types/{id}/      # Update category type
DELETE /api/v1/category-types/{id}/      # Delete category type (soft delete)
GET    /api/v1/category-types/{id}/categories/  # Get categories under this type
```

## **3. Categories Endpoints**
```
GET    /api/v1/categories/               # List all categories (paginated)
POST   /api/v1/categories/               # Create new category
GET    /api/v1/categories/{id}/          # Get category by ID
PUT    /api/v1/categories/{id}/          # Update category
DELETE /api/v1/categories/{id}/          # Delete category (soft delete)
GET    /api/v1/categories/{id}/products/ # Get products under this category
GET    /api/v1/categories/by-type/{type_id}/ # Get categories by type
```

## **4. Suppliers Endpoints**
```
GET    /api/v1/suppliers/                # List all suppliers (paginated)
POST   /api/v1/suppliers/                # Create new supplier
GET    /api/v1/suppliers/{id}/           # Get supplier by ID
PUT    /api/v1/suppliers/{id}/           # Update supplier
DELETE /api/v1/suppliers/{id}/           # Delete supplier (soft delete)
GET    /api/v1/suppliers/{id}/products/  # Get products from this supplier
```

## **5. Attributes Endpoints**
```
GET    /api/v1/attributes/               # List all attributes (paginated)
POST   /api/v1/attributes/               # Create new attribute
GET    /api/v1/attributes/{id}/          # Get attribute by ID
PUT    /api/v1/attributes/{id}/          # Update attribute
DELETE /api/v1/attributes/{id}/          # Delete attribute (soft delete)
```

## **6. Products Endpoints**
```
GET    /api/v1/products/                 # List all products (paginated)
POST   /api/v1/products/                 # Create new product
GET    /api/v1/products/{id}/            # Get product by ID
PUT    /api/v1/products/{id}/            # Update product
DELETE /api/v1/products/{id}/            # Delete product (soft delete)
GET    /api/v1/products/{id}/skus/       # Get SKUs for this product
```

## **7. SKUs Endpoints**
```
GET    /api/v1/skus/                     # List all SKUs (paginated)
POST   /api/v1/skus/                     # Create new SKU
GET    /api/v1/skus/{id}/                # Get SKU by ID
PUT    /api/v1/skus/{id}/                # Update SKU
DELETE /api/v1/skus/{id}/                # Delete SKU (soft delete)
GET    /api/v1/skus/{id}/prices/         # Get price details for this SKU
```

## **8. Pricelists Endpoints**
```
GET    /api/v1/pricelists/               # List all pricelists (paginated)
POST   /api/v1/pricelists/               # Create new pricelist
GET    /api/v1/pricelists/{id}/          # Get pricelist by ID
PUT    /api/v1/pricelists/{id}/          # Update pricelist
DELETE /api/v1/pricelists/{id}/          # Delete pricelist (soft delete)
GET    /api/v1/pricelists/{id}/prices/   # Get price details for this pricelist
```

## **9. Price Details Endpoints**
```
GET    /api/v1/price-details/            # List all price details (paginated)
POST   /api/v1/price-details/            # Create new price detail
GET    /api/v1/price-details/{id}/       # Get price detail by ID
PUT    /api/v1/price-details/{id}/       # Update price detail
DELETE /api/v1/price-details/{id}/       # Delete price detail (soft delete)
```

## **10. Images Endpoints**
```
GET    /api/v1/images/                   # List all images (paginated)
POST   /api/v1/images/                   # Upload new image
GET    /api/v1/images/{id}/              # Get image by ID
PUT    /api/v1/images/{id}/              # Update image metadata
DELETE /api/v1/images/{id}/              # Delete image
```

## **11. Authentication Endpoints**
```
POST   /api/v1/auth/login/               # User login
POST   /api/v1/auth/logout/              # User logout
POST   /api/v1/auth/refresh/             # Refresh access token
GET    /api/v1/auth/me/                  # Get current user info
POST   /api/v1/auth/forgot-password/     # Request password reset
POST   /api/v1/auth/reset-password/      # Reset password with token
POST   /api/v1/auth/verify-token/        # Verify token validity
```

## **12. Dashboard/Analytics Endpoints**
```
GET    /api/v1/dashboard/stats/          # Get dashboard statistics
GET    /api/v1/dashboard/recent-products/ # Get recently added products
GET    /api/v1/dashboard/low-stock/      # Get low stock alerts
GET    /api/v1/analytics/products/       # Product analytics
GET    /api/v1/analytics/categories/     # Category analytics
GET    /api/v1/analytics/suppliers/      # Supplier analytics
```

# Response Format
```python
# Success response
{
    "success": true,
    "data": {...},
    "error": None
}
```

# Pagination
Implement pagination for list endpoints with these parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort_field`: Field to sort by
- `order_rule`: Sort order (asc/desc, default: asc)

Include pagination metadata in responses:
```
{
  "success": true,
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 157,
    "pages": 8
  },
  "error": null
}
```

# Error response
```
{
    "success": false,
    "data": None
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {...}
    }
}
```
# Filtering
- Simple filter: `?filter[field]=value`
- Operator filter: `?filter[field][operator]=value`
- Supported operators: `gt`, `lt`, `ge`, `le`, `ne`, `like`