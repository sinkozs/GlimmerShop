# Headless e-commerce CMS

A flexible, high-performance e-commerce Content Management System built with FastAPI, offering a headless architecture for maximum customization and scalability. While currently configured for jewelry products, the system is designed to be easily adaptable for any product category.

## Key Features

- **Headless Architecture**: Decoupled backend allowing integration with any frontend technology
- **Async Performance**: Built on FastAPI and async SQLAlchemy for optimal performance
- **Flexible Product Management**: Easily customizable product schemas and categories
- **Secure Authentication**: JWT-based authentication with role-based access control
- **Payment Processing**: Stripe integration for secure payments
- **Seller Analytics**: Custom Stripe metadata configuration providing detailed sales insights
- **Database Management**: PostgreSQL with Alembic migrations for reliable data persistence
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Testing**: Integration tests using pytest
- **CI/CD Pipeline**: GitHub Actions workflows for:
  - Code quality checks (Black formatter and Flake8 linter)
  - Automated integration test runs on every push

#### Security Features

- Custom HTTP-only cookie implementation
- Secure session management
- JWT token handling
- Configurable session expiration
- Role-based access control (User/Seller)
- TODO: Cross-Site Request Forgery (CSRF) protection

## Architecture

### Backend (Core Focus)
- **FastAPI 0.103+** - Modern web framework
- **SQLAlchemy 2.0+** - SQL toolkit and ORM
- **Alembic 1.8+** - Database migration tool
- **Pydantic 2.5+** - Data validation
- **asyncpg 0.29+** - Async PostgreSQL driver
- **aioredis 2.0+** - Async Redis client
- **Stripe 10.5+** - Payment processing
- **Pillow 10.4+** - Image processing
- **python-jose 3.3+** - JWT token handling
- **pytest 8.3+** - Testing framework


### Frontend (Demo Implementation)
- **Framework**: React
- **Purpose**: Demonstration of API integration and workflow visualization
- Note: The frontend implementation serves as a reference and is not intended for production use

### Development Tools
- uvicorn 0.20+ - ASGI server
- black - Code formatting
- flake8 - Code linting
- pytest-asyncio - Async testing support


## Quick Start

#### Prerequisites

- Python 3.12+
- PostgreSQL 12+
- Redis 5+
- Node.js 18+ (for frontend demo)


