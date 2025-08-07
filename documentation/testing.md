# Test Structure
```
/tests
├── /api                        # API layer tests (52 test files total)
│   ├── /v1
│   │   ├── /endpoints          # Individual endpoint tests (10 files)
│   │   │   ├── test_auth_endpoint.py
│   │   │   ├── test_user_endpoint.py
│   │   │   ├── test_profile_endpoint.py
│   │   │   ├── test_attribute_endpoint.py
│   │   │   ├── test_category_type_endpoint.py
│   │   │   ├── test_category_endpoint.py
│   │   │   ├── test_product_endpoint.py
│   │   │   ├── test_sku_endpoint.py
│   │   │   ├── test_supplier_endpoint.py
│   │   │   └── test_pricelist_endpoint.py
├── /core                       # Core functionality tests
│   ├── test_mixins.py
│   └── test_session.py
├── /common                     # Generic/reusable tests
│   ├── test_base_model.py
│   ├── test_base_schema.py
│   ├── test_common_operation_endpoint.py
│   ├── test_common_operation_model.py
│   ├── test_common_operation_schema.py
│   ├── test_constraint_endpoint.py
│   ├── test_constraint_model.py
│   ├── test_constraint_schema.py
│   ├── test_data_type_endpoint.py
│   ├── test_data_type_model.py
│   └── test_data_type_schema.py
├── /models                     # SQLAlchemy model tests (11 files)
│   ├── test_user_model.py
│   ├── test_attribute_model.py
│   ├── test_category_type_model.py
│   ├── test_category_model.py
│   ├── test_product_model.py
│   ├── test_sku_model.py
│   ├── test_supplier_model.py
│   ├── test_pricelist_model.py
│   ├── test_price_detail_model.py
│   ├── test_sku_attribute_value_model.py
│   └── test_image_model.py
├── /schemas                    # Pydantic schema tests (9 files)
│   ├── test_user_schema.py
│   ├── test_attribute_schema.py
│   ├── test_category_type_schema.py
│   ├── test_category_schema.py
│   ├── test_product_schema.py
│   ├── test_sku_schema.py
│   ├── test_supplier_schema.py
│   ├── test_pricelist_schema.py
│   └── test_image_schema.py
├── /utils                      # Test utility functions
│   └── model_test_utils.py     # Database operation helpers
├── /fixtures                   # Test data factories and fixtures
│   ├── __init__.py
│   ├── model_factories.py      # Factory functions for creating test data
│   └── auth_headers_factories.py # Authentication fixtures
├── conftest.py                 # Global test configuration and database setup
└── test_main.py                # FastAPI application tests
```

## Testing Strategy

This project implements a **comprehensive multi-layered testing approach** that ensures high coverage across all application layers while maintaining test efficiency and maintainability.

### **Current Test Coverage: 52 Test Files**
- **API Endpoints**: 10 comprehensive endpoint test files
- **Models**: 11 SQLAlchemy model test files  
- **Schemas**: 9 Pydantic schema validation test files
- **Common/Generic**: 11 reusable test files for shared functionality
- **Core**: 2 core functionality test files
- **Utils**: 1 testing utility file
- **Integration**: Embedded within endpoint tests

## **Testing Layers**

### 1. **API Endpoint Tests** (`/api/v1/endpoints/`)
Comprehensive testing of all REST API endpoints with focus on:

**Authentication & Authorization:**
- JWT token validation
- Role-based access control (USER, ADMIN, MANAGER, SYSTEM)
- Permission-based resource access
- Ownership-based operations

**CRUD Operations:**
- Create, Read, Update, Delete operations
- Bulk operations and filtering
- Pagination with skip/limit parameters
- Search and filter functionality

**Integration Workflows:**
- Complete CRUD workflows (Create → Read → Update → Delete)
- Multi-step business processes
- Cross-endpoint data consistency
- Error handling and edge cases

**Example from `test_user_endpoint.py`:**
```python
class TestUserEndpointIntegration:
    async def test_full_crud_workflow(self, async_client, auth_headers_admin):
        # Create → Read → Update → Delete workflow
```

### 2. **Model Tests** (`/models/`)
Focused on SQLAlchemy model behavior and database operations:

**Model Initialization:**
- Field validation and constraints
- Default value assignment
- Relationship configuration
- Custom property methods

**Database Operations:**
- CRUD operations with proper transaction handling
- Complex relationship testing
- Cascade behavior validation
- Custom model methods and properties

**Business Logic:**
- Model-specific validation rules
- Custom field processing (slug generation, etc.)
- Computed properties and methods

### 3. **Schema Tests** (`/schemas/`)
Pydantic schema validation and serialization testing:

**Input Validation:**
- Required field validation
- Data type validation
- Custom validator functions
- Field constraints (min/max length, patterns)

**Serialization/Deserialization:**
- Model to schema conversion
- Schema to model conversion
- Nested schema handling
- Custom field transformations

### 4. **Common/Generic Tests** (`/common/`)
Reusable tests that apply to all models and schemas:

**Base Functionality:**
- Base model inheritance testing
- Common field validation
- Standard CRUD operations
- Database constraint testing

**Data Type Validation:**
- String, Integer, Boolean, Float validation
- DateTime handling and timezone support
- JSONB field operations
- Enum field validation

### 5. **Core Tests** (`/core/`)
Testing of core application functionality:

**Session Management:**
- Database connection handling
- Transaction management
- Async session behavior

**Utility Functions:**
- Mixin functionality
- Helper utilities
- Configuration validation

## **Testing Utilities & Fixtures**

### **Authentication Fixtures** (`/fixtures/auth_headers_factories.py`)
```python
@pytest.fixture
async def auth_headers_admin(db_session):
    # Creates admin user and returns auth headers
    
@pytest.fixture  
async def auth_headers_user(db_session):
    # Creates regular user and returns auth headers
```

### **Model Factories** (`/fixtures/model_factories.py`)
Factory functions for creating test data with proper relationships and realistic data.

### **Test Utilities** (`/utils/model_test_utils.py`)
Common database operations for testing:
```python
async def save_object(session, object)
async def get_object_by_id(session, model_class, object_id)
async def get_all_objects(session, model_class)
async def delete_object(session, object)
async def count_model_objects(session, model_class)
def assert_relationship(model_class, relationship_name, back_populates)
```

## **Test Configuration**

### **Database Setup** (`conftest.py`)
- **Session-scoped test database** creation/teardown
- **Async session management** with proper cleanup
- **Factory fixture imports** for easy test data creation
- **Real PostgreSQL database** for integration testing

### **Async Testing** (`pytest.ini`)
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
pythonpath = .
```

## **Testing Best Practices Implemented**

### **1. Comprehensive Coverage**
- **Every endpoint** has full CRUD testing
- **Every model** has initialization and relationship testing  
- **Every schema** has validation and serialization testing
- **Integration workflows** test real-world usage patterns

### **2. Realistic Test Data**
- **Factory pattern** for consistent test data creation
- **Proper relationships** between test entities
- **Edge cases and error scenarios** coverage

### **3. Authentication Testing**
- **Role-based access control** validation
- **JWT token handling** in all protected endpoints
- **Permission boundary** testing

### **4. Database Integrity**
- **Real database transactions** with proper rollback
- **Relationship integrity** validation
- **Constraint testing** for data consistency

### **5. Error Handling**
- **HTTP status code** validation
- **Error message** consistency testing
- **Exception handling** verification

## **Test Execution**

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

This testing strategy ensures **high confidence** in the application's reliability, **comprehensive coverage** of all functionality, and **maintainable test code** that grows with the application.
