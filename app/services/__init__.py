# Import all services for centralized access
from app.services.category_service import category_service
from app.services.category_type_service import category_type_service
from app.services.supplier_service import supplier_service
from app.services.product_service import product_service
from app.services.sku_service import sku_service

# Export all services
__all__ = [
    "category_service",
    "category_type_service",
    "supplier_service",
    "product_service",
    "sku_service",
]
