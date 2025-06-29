# Test Structure
```
/tests
├── /api
│   ├── /v1
│   │   ├── /endpoints          # Test individual endpoint files
│   │   │   ├── test_endpoints_file.py (example)
│   │   │   ├── the other file ...
│   │   └── /dependencies       # Test API dependencies
│   │       ├── test_dependencies_file.py (example)
│   │       └── the other file ...
├── /core                       # Test core functionality
│   ├── test_config.py
│   ├── test_common_operation.py
│   ├── test_constraint.py
│   ├── test_data_type.py
│   ├── test_security.py
│   ├── test_session.py
│   ├── test_exceptions.py
│   └── test_base.py
├── /models                     # Test SQLAlchemy models
│   ├── test_model_file.py (example)
│   ├── the other file ...
├── /schemas                    # Test Pydantic schemas
│   ├── test_schema_file.py (example)
│   ├── the other file ...
├── /services                   # Test business logic
│   ├── test_service_file.py (example)
│   ├── the other file ...
├── /repositories               # Test data access layer
│   ├── test_repository_file.py (example)
│   ├── the other file ...
├── /utils                      # Test utility functions
│   ├── test_utils_file.py (example)
│   ├── the other file ...
├── /integration                # Integration tests
│   ├── test_intergration_file.py (example)
│   ├── the other file ...
├── /fixtures                   # Test data factories
│   ├── __init__.py
│   ├── fixture_file.py (example)
│   ├── the other file ...
├── conftest.py                 # Global test configuration
├── test_main.py                # Main app tests
```

## Testing Strategy

This project implements a **DRY (Don't Repeat Yourself) testing approach** to minimize code duplication and maximize test efficiency. Instead of writing repetitive tests for every model, we focus on two main testing layers:

### 1. **Generic/Common Tests** (`/core` directory)
These tests cover functionality that applies to **all models** in the system:

- **`test_base.py`** - Tests Base model inheritance, field configuration, table name generation, and common model behavior
- **`test_common_operation.py`** - Tests database operations like bulk creation, rollback scenarios, and transaction handling
- **`test_data_type.py`** - Tests data type validation for String, Integer, Boolean, Float, DateTime, and JSONB fields
- **`test_constraint.py`** - Tests database constraints and validation rules
- **`test_session.py`** - Tests database session management and connection handling

These tests ensure that every model inheriting from `Base` automatically gets tested for common functionality without writing duplicate test code.

### 2. **Model-Specific Tests** (`/models` directory)
These tests focus **only on unique features** specific to each model:

- **Business logic specific to the model**
- **Custom validation rules**
- **Unique field properties and constraints**
- **Model-specific relationships**
- **Custom methods and behaviors**

For example, `test_category_type.py` only tests:
- Model initialization and field assignment
- CRUD operations (Create, Read, Update, Delete) specific to the model
- Slug generation from name field
- Specific field properties (length, uniqueness)
- CategoryType-specific string representation
- Model-specific listeners and events

### 3. **Utility Functions** (`/utils` directory)
- **`model_test_utils.py`** - Provides reusable functions for common database operations like `save_object()`, `get_object_by_id()`, `delete_object()`, etc.
- **Relationship testing utilities** - Helper functions to test model relationships

### 4. **Model Initialization and CRUD Testing**
Every model test should include comprehensive testing of:

**Initialization Testing:**
- Model instantiation with valid data
- Field assignment and default values
- String representation (`__str__` and `__repr__` methods)
- Model inheritance verification

**CRUD Operations Testing:**
- **Create**: Test object creation with various data combinations
- **Read**: Test retrieval by ID and bulk retrieval operations
- **Update**: Test field modifications and data persistence
- **Delete**: Test object deletion and cascade behavior

**Standard Test Pattern:**
```python
async def test_create_operation(self, db_session):
    """Test the create operation"""
    item = ModelName(field="value")
    await save_object(db_session, item)
    
    # Assert ID is assigned (incremental based on existing objects)
    assert item.id == 1  # or 2, 3, etc. based on existing test data
    
    # Assert all model-specific fields (exclude Base model fields)
    assert item.field == "value"
    assert item.other_field == "expected_value"
    # ... assert all other model-specific fields

async def test_get_operation(self, db_session):
    """Test the get operation"""
    item = await get_object_by_id(db_session, ModelName, item_id)
    
    # Assert all model-specific fields are retrieved correctly
    assert item.field == "expected_value"
    assert item.other_field == "expected_value"
    # ... assert all other model-specific fields

async def test_update_operation(self, db_session):
    """Test the update operation"""
    item.field = "new_value"
    await save_object(db_session, item)
    
    # Assert updated fields and unchanged fields
    assert item.field == "new_value"
    assert item.other_field == "unchanged_value"  # Verify other fields remain unchanged

async def test_delete_operation(self, db_session):
    """Test the delete operation"""
    await delete_object(db_session, item)
    deleted_item = await get_object_by_id(db_session, ModelName, item_id)
    assert deleted_item is None
```

**Important Notes:**
- **ID Assertion**: Always assert the specific ID value (1, 2, 3, etc.) based on the count of existing objects in your test setup
- **Field Coverage**: Assert ALL model-specific fields in each test, excluding Base model fields (`id`, `created_at`, `updated_at`, `created_by`, `updated_by`, `is_active`, `sequence`)
- **Complete Validation**: Ensure every custom field defined in your model is properly tested and validated

### Benefits of This Approach:
- **Reduced code duplication** - Common functionality is tested once in `/core`
- **Faster test development** - New models only need tests for their unique features
- **Better maintainability** - Changes to common functionality only require updates in one place
- **Comprehensive coverage** - All models get tested for both common and specific functionality
- **Clear separation of concerns** - Generic vs specific test logic is clearly separated