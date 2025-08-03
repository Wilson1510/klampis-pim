# Import all repositories for centralized access
# from app.repositories.user import user  # Commented out due to missing user schema
from app.repositories.category_repository import category_repository
from app.repositories.category_type_repository import category_type_repository
from app.repositories.supplier_repository import supplier_repository
from app.repositories.product_repository import product_repository
from app.repositories.sku_repository import sku_repository

# Export all repositories
__all__ = [
    # "user",  # Commented out due to missing user schema
    "category_repository",
    "category_type_repository",
    "supplier_repository",
    "product_repository",
    "sku_repository",
]
