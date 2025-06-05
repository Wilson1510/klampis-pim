# Basic Requirements
- Python 3.11
- FastAPI 0.115.12
- SQLAlchemy 2.0
- Pydantic 2.11

# Project Structure
```
app/
├── api/                    # API layer
│   ├── v1/                # API version 1
│   │   ├── endpoints/     # Route handlers
│   │   └── dependencies/  # Route dependencies
├── core/                  # Core configuration
│   ├── config.py         # Settings and configuration
│   ├── security.py       # Authentication & authorization
│   ├── session.py        # Database connection and sessions
│   ├── exceptions.py     # Custom exception classes and error handlers
│   └── base.py           # Base classes and common utilities
├── models/               # SQLAlchemy models
├── schemas/              # Pydantic schemas
├── services/             # Business logic layer
├── repositories/         # Data access layer
├── utils/                # Utility functions
└── main.py              # FastAPI application entry point
```

# Audit Trail Strategy
- System user with (ID: 1) will be created for all automated operations
- `created_by` and `updated_by` will be used as non-nullable foreign keys
- Default to system user (ID: 1) when no user context is available
- System user has role "SYSTEM"
- All data migrations and seeding operations use system user

# Create .env, test_config.py, and alembic.ini file
1. Copy configuration files:
   ```bash
   cp env.example .env
   cp test_config.example tests/core/test_config.py
   cp alembic.example alembic.ini
   ```
   cp for linux, copy for windows
2. Update database password in all copied files by changing `yourpassword`