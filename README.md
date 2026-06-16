# Document Intelligence Agent Platform

**Enterprise-grade policy-governed document management powered by multi-agent AI workflows**

> Transform document review from manual, error-prone processes to intelligent, policy-governed automation with full audit trails and supervisor approvals.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.20-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Multi-LLM](https://img.shields.io/badge/LLM-OpenAI%20%7C%20Gemini%20%7C%20Anthropic-purple.svg)]()

---

## 🎯 What Is This?

This platform demonstrates the intersection of three powerful domains:

1. **Document Intelligence** (Evisort-style) - AI-powered document analysis, extraction, and risk assessment
2. **Agent Orchestration** - Multi-agent workflows with LangGraph for complex, stateful operations
3. **Enterprise Governance** (Workday-style) - Multi-tenancy, RBAC, policy compliance, and audit logging

### Key Differentiators

✅ **Custom Agent Factory** - Users create specialized agents without coding
✅ **Policy-Based Evaluation** - Documents evaluated against company policies with full citations
✅ **Human-in-the-Loop** - Supervisor approvals via Slack/Email/Discord
✅ **Context Validation** - User insights validated against policies automatically
✅ **Multi-Channel Notifications** - Interactive approval workflows
✅ **Complete Audit Trail** - Every action logged, immutable, traceable
✅ **Multi-LLM Support** - OpenAI, Google Gemini, and Anthropic Claude

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         FastAPI Backend (Async)             │
│  - Request routing                          │
│  - RBAC enforcement                         │
│  - Multi-tenancy                            │
└───┬──────────┬────────────┬────────┬────────┘
    │          │            │        │
    ▼          ▼            ▼        ▼
┌────────┐ ┌───────┐ ┌──────────┐ ┌──────────┐
│Extract │ │Risk   │ │Comparison│ │Q&A       │
│Agent   │ │Agent  │ │Agent     │ │Agent     │
└───┬────┘ └───┬───┘ └────┬─────┘ └────┬─────┘
    │          │           │            │
    └──────────┴───────────┴────────────┘
               │
    ┌──────────▼──────────────┐
    │ Policy Evaluation Engine│
    │ - Full citation system  │
    │ - Violation detection   │
    │ - Compliance scoring    │
    └──────────┬──────────────┘
               │
    ┌──────────▼──────────────┐
    │ Human-in-the-Loop       │
    │ - Context validation    │
    │ - Approval workflows    │
    │ - Multi-channel notify  │
    └─────────────────────────┘
               │
    ┌──────────┴─────────┬────────────┐
    │                    │            │
┌───▼────┐ ┌──────▼─────┐ ┌────▼────┐
│RDS     │ │ Qdrant     │ │ S3      │
│Postgres│ │ (Vectors)  │ │ (Docs)  │
└────────┘ └────────────┘ └─────────┘
```

---

## 🚀 Complete Production-Ready FastAPI Application with LangGraph Multi-Agent System

## Features

- FastAPI framework with automatic API documentation
- SQLAlchemy ORM with Alembic migrations
- JWT-based authentication
- User and Item management
- Pydantic schemas for request/response validation
- Comprehensive test suite with pytest
- CORS middleware
- Logging configuration
- Environment-based configuration

## Project Structure

```
docuengine/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       └── items.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base_class.py
│   │   ├── session.py
│   │   └── init_db.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── item.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── dependencies.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_main.py
│   │   ├── test_auth.py
│   │   ├── test_users.py
│   │   └── test_items.py
│   ├── __init__.py
│   └── main.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── README
├── logs/
├── .env.example
├── .gitignore
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd docuengine
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
alembic upgrade head
```

## Running the Application

### Development Server

Start the development server with auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/api/v1/openapi.json

### Production Server

For production, use Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

### View migration history

```bash
alembic history
```

## Testing

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

Run specific test file:

```bash
pytest app/tests/test_main.py
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token
- `POST /api/v1/auth/refresh` - Refresh access token

### Users

- `GET /api/v1/users/` - Get list of users
- `GET /api/v1/users/me` - Get current user information
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Items

- `GET /api/v1/items/` - Get list of items
- `GET /api/v1/items/{item_id}` - Get item by ID
- `POST /api/v1/items/` - Create new item (requires authentication)
- `PUT /api/v1/items/{item_id}` - Update item (requires authentication)
- `DELETE /api/v1/items/{item_id}` - Delete item (requires authentication)

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `PROJECT_NAME` - Application name
- `VERSION` - Application version
- `SECRET_KEY` - Secret key for JWT tokens
- `DATABASE_URL` - Database connection URL
- `ALLOWED_ORIGINS` - CORS allowed origins
- `DEBUG` - Debug mode (True/False)
- `ENVIRONMENT` - Environment (development/production)

## Development

### Code Formatting

Format code with Black:

```bash
black app/
```

### Linting

Lint code with Flake8:

```bash
flake8 app/
```

### Type Checking

Check types with MyPy:

```bash
mypy app/
```

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- CORS middleware configured
- Environment variables for sensitive data
- SQL injection prevention through SQLAlchemy ORM

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
