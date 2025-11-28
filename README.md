# 🏪 KLAMPIS PIM - Product Information Management System

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.41-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tests](https://img.shields.io/badge/tests-52_files-brightgreen.svg)

A modern, scalable Product Information Management (PIM) system built for large supermarkets and retail chains. Manage products, categories, suppliers, pricing, and inventory with enterprise-grade features.

## ✨ Features

### 🔐 **Authentication & Authorization**
- JWT-based authentication with refresh token support
- Role-based access control (USER, ADMIN, MANAGER, SYSTEM)
- Secure password hashing with Argon2
- Token rotation for enhanced security

### 📦 **Product Management**
- Hierarchical category system with unlimited nesting
- Product variants (SKUs) with dynamic attributes
- Image management with multiple images per product
- Flexible attribute system for product specifications

### 💰 **Pricing & Inventory**
- Multi-tier pricing system with pricelists
- Quantity-based pricing rules
- Supplier management and product sourcing
- Price history and tracking

### 🏗️ **Architecture**
- Clean Architecture with Repository Pattern
- Async/await support for high performance
- Comprehensive API documentation with OpenAPI
- Database migrations with Alembic

## 🚀 Quick Start

### 🐳 Docker Quick Start (Recommended)

The fastest way to get the application running is using Docker. We provide a setup script that automates the build process, database migrations, and initial user creation.

1. **Run the setup script:**
   ```bash
   chmod +x docker-setup.sh
   ./docker-setup.sh

2. **Manual Docker Commands (Alternative): If you prefer running commands manually:**
# Start services
docker-compose up -d

# Run database migrations
docker-compose exec app alembic upgrade head

# Create system & admin users
docker-compose exec app python scripts/create_initial_user.py

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/klampis-pim.git
cd klampis-pim
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp env.example .env
# Edit .env with your database credentials and settings
```

5. **Setup database**
```bash
# Create database
createdb klampis_pim

# Run migrations
alembic upgrade head
```

6. **Create initial user**
```bash
python scripts/create_initial_user.py
```

7. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API Docs (Swagger)**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/openapi.json`

## 🏗️ Project Structure

```
klampis-pim/
├── app/
│   ├── api/                    # API layer
│   │   └── v1/
│   │       ├── endpoints/      # Route handlers
│   │       └── dependencies/   # Route dependencies
│   ├── core/                   # Core configuration
│   │   ├── config.py          # Settings
│   │   ├── security.py        # Authentication
│   │   ├── session.py         # Database sessions
│   │   └── exceptions.py      # Error handling
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   ├── repositories/           # Data access layer
│   └── utils/                  # Utilities
├── tests/                      # Test suite (52 files)
├── documentation/              # Project documentation
├── alembic/                    # Database migrations
└── scripts/                    # Utility scripts
```

## 🗄️ Database Schema

The system uses a comprehensive database schema with the following main entities:

- **Users** - System users with role-based permissions
- **Categories** - Hierarchical product categorization
- **Products** - Main product information
- **SKUs** - Product variants with attributes
- **Suppliers** - Supplier management
- **Pricelists** - Pricing management
- **Attributes** - Dynamic product specifications

## 🔧 Configuration

Key configuration options in `.env`:

```env
# Database
DATABASE_URI=postgresql+asyncpg://user:pass@localhost/klampis_pim

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API
API_V1_PREFIX=/api
PROJECT_NAME=KLAMPIS PIM
VERSION=1.0.0

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## 🧪 Testing

The project includes comprehensive test coverage with 52 test files:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/api/          # API tests
pytest tests/models/       # Model tests
pytest tests/schemas/      # Schema tests
```

**Test Coverage:**
- ✅ 10 API endpoint test files
- ✅ 11 SQLAlchemy model tests
- ✅ 9 Pydantic schema tests
- ✅ Authentication & authorization
- ✅ Integration workflows
- ✅ Error handling

## 📖 API Usage Examples

### Authentication
```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Products
```bash
# Get products with filtering
curl -X GET "http://localhost:8000/api/products?category_id=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create product
curl -X POST "http://localhost:8000/api/products" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Premium Coffee",
    "slug": "premium-coffee",
    "description": "High quality arabica coffee",
    "category_id": 1,
    "supplier_id": 1
  }'
```

## 🔒 Security Features

- **JWT Authentication** with refresh token rotation
- **Argon2 password hashing** (more secure than bcrypt)
- **Role-based access control** with 4 permission levels
- **Input validation** with Pydantic schemas
- **SQL injection prevention** with parameterized queries
- **CORS configuration** for cross-origin requests


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Use conventional commit messages
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Authentication**: JWT with refresh tokens
- **Validation**: Pydantic V2
- **Testing**: pytest with async support
- **Documentation**: OpenAPI/Swagger
- **Migrations**: Alembic

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check the [documentation](documentation/) folder
- Review the API documentation at `/docs`

**Built with ❤️ for modern retail management**
