# Endpoint Structure
Organize endpoints by resource type, following RESTful conventions:

## **1. Users Endpoints**
```
GET    /api/v1/users/                    # List all users (paginated)
POST   /api/v1/users/                    # Create new user
GET    /api/v1/users/{id}/               # Get user by ID
PUT    /api/v1/users/{id}/               # Update user
DELETE /api/v1/users/{id}/               # Delete user
```

## **2. Category Types Endpoints**
```
GET    /api/v1/category-types/           # List all category types (paginated)
POST   /api/v1/category-types/           # Create new category type
GET    /api/v1/category-types/{id}/      # Get category type by ID
PUT    /api/v1/category-types/{id}/      # Update category type
DELETE /api/v1/category-types/{id}/      # Delete category type
GET    /api/v1/category-types/{id}/categories/  # Get categories under this type
```

## **3. Categories Endpoints**
```
GET    /api/v1/categories/               # List all categories (paginated)
POST   /api/v1/categories/               # Create new category
GET    /api/v1/categories/{id}/          # Get category by ID
PUT    /api/v1/categories/{id}/          # Update category
DELETE /api/v1/categories/{id}/          # Delete category
GET    /api/v1/categories/{id}/products/ # Get products under this category
GET    /api/v1/categories/{id}/children/ # Get all children of this category
```

## **4. Suppliers Endpoints**
```
GET    /api/v1/suppliers/                # List all suppliers (paginated)
POST   /api/v1/suppliers/                # Create new supplier
GET    /api/v1/suppliers/{id}/           # Get supplier by ID
PUT    /api/v1/suppliers/{id}/           # Update supplier
DELETE /api/v1/suppliers/{id}/           # Delete supplier
GET    /api/v1/suppliers/{id}/products/  # Get products from this supplier
```

## **5. Attributes Endpoints**
```
GET    /api/v1/attributes/               # List all attributes (paginated)
POST   /api/v1/attributes/               # Create new attribute
GET    /api/v1/attributes/{id}/          # Get attribute by ID
PUT    /api/v1/attributes/{id}/          # Update attribute
DELETE /api/v1/attributes/{id}/          # Delete attribute
```

## **6. Products Endpoints**
```
GET    /api/v1/products/                 # List all products (paginated)
POST   /api/v1/products/                 # Create new product
GET    /api/v1/products/{id}/            # Get product by ID
PUT    /api/v1/products/{id}/            # Update product
DELETE /api/v1/products/{id}/            # Delete product
GET    /api/v1/products/{id}/skus/       # Get SKUs for this product
```

## **7. SKUs Endpoints**
```
GET    /api/v1/skus/                     # List all SKUs (paginated)
POST   /api/v1/skus/                     # Create new SKU
GET    /api/v1/skus/{id}/                # Get SKU by ID
PUT    /api/v1/skus/{id}/                # Update SKU
DELETE /api/v1/skus/{id}/                # Delete SKU
```

## **8. Pricelists Endpoints**
```
GET    /api/v1/pricelists/               # List all pricelists (paginated)
POST   /api/v1/pricelists/               # Create new pricelist
GET    /api/v1/pricelists/{id}/          # Get pricelist by ID
PUT    /api/v1/pricelists/{id}/          # Update pricelist
DELETE /api/v1/pricelists/{id}/          # Delete pricelist
```

## **9. Authentication Endpoints**
```
POST   /api/v1/auth/login/               # User login
POST   /api/v1/auth/logout/              # User logout
POST   /api/v1/auth/refresh/             # Refresh access token
```

## **10. Profile Endpoints**
GET    /api/v1/profile/me/               # Get current user info
PUT    /api/v1/profile/me/               # Update current user profile
POST   /api/v1/profile/change-password/  # Reset password with token
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