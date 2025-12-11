# 🚀 FastAPI Task Management System

A production-ready task management API built with FastAPI, featuring JWT authentication, Redis caching, rate limiting, and comprehensive testing.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Getting Started](#-getting-started)
- [API Endpoints](#-api-endpoints)
- [Design Patterns & Principles](#-design-patterns--principles)
- [Key Implementation Details](#-key-implementation-details)
- [Testing](#-testing)
- [Docker Deployment](#-docker-deployment)
- [Contact](#-contact)

---

## ✨ Features

### 🔐 Authentication & Security
- **JWT-based authentication** with secure token generation
- **Password hashing** using bcrypt
- **OAuth2 compatible** login for Swagger UI
- **User registration & login** endpoints
- **Protected routes** with dependency injection

### 📝 Task Management
- **Full CRUD operations** for tasks
- **Advanced filtering** by priority, status, and search term
- **Pagination support** for large datasets
- **Task statistics** dashboard endpoint
- **User-specific tasks** with ownership tracking

### 📁 File Management
- **File upload** with validation (type and size checks)
- **Secure file download** with permission checks
- **File deletion** for authorized users
- **Support for multiple formats**: txt, pdf, png, jpg, gif, doc, docx
- **5MB file size limit** enforcement

### ⚡ Performance & Scalability
- **Redis caching** for frequently accessed data
- **Rate limiting** (strict & moderate tiers)
- **Async/await** throughout for optimal performance
- **Connection pooling** for database operations
- **Cache invalidation** strategies

### 🏥 Monitoring & DevOps
- **Health check endpoints** for monitoring
- **Structured logging** with emojis for visibility
- **Docker containerization** with multi-service setup
- **Database migrations** with Alembic
- **Environment-based configuration** (.env support)

### 🧪 Developer Experience
- **Type hints** everywhere for better IDE support
- **Automatic API documentation** (Swagger & ReDoc)
- **Comprehensive test suite** with pytest
- **Hot reload** in development mode
- **Clean separation of concerns** (routers, CRUD, models)

---

## 🛠 Tech Stack

```mermaid
graph TB
    A[FastAPI] --> B[PostgreSQL]
    A --> C[Redis]
    A --> D[Alembic]
    A --> E[SQLAlchemy]
    A --> F[Pydantic]
    G[Docker] --> A
    G --> B
    G --> C
    H[pytest] -.-> A
```

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI | High-performance async web framework |
| **Database** | PostgreSQL + asyncpg | Async relational database |
| **ORM** | SQLAlchemy 2.0 | Database abstraction layer |
| **Cache** | Redis | In-memory caching & rate limiting |
| **Auth** | python-jose + passlib | JWT tokens & password hashing |
| **Validation** | Pydantic | Data validation & settings |
| **Migration** | Alembic | Database schema versioning |
| **Testing** | pytest + httpx | Async testing framework |
| **Containerization** | Docker + Docker Compose | Service orchestration |

---

## 🏗 Project Architecture

```
fastapi_project/
├── 📁 src/app/              # Application source code
│   ├── main.py             # FastAPI app initialization & middleware
│   ├── 📁 api/             # API dependencies
│   │   └── deps.py         # Dependency injection (DB, auth)
│   ├── 📁 core/            # Core functionality
│   │   ├── config.py       # Settings management (Pydantic)
│   │   ├── database.py     # Async SQLAlchemy engine
│   │   ├── security.py     # JWT & password utilities
│   │   ├── cache.py        # Redis cache manager
│   │   ├── rate_limiter.py # Rate limiting logic
│   │   └── decorators.py   # Custom caching decorators
│   ├── 📁 models/          # Data models
│   │   ├── database.py     # SQLAlchemy ORM models
│   │   ├── user.py         # Pydantic user schemas
│   │   └── task.py         # Pydantic task schemas
│   ├── 📁 crud/            # Database operations
│   │   ├── base.py         # Generic CRUD operations
│   │   ├── user.py         # User-specific queries
│   │   └── task.py         # Task-specific queries
│   └── 📁 routers/         # API endpoints
│       ├── auth.py         # Login & registration
│       ├── tasks.py        # Task CRUD operations
│       ├── files.py        # File upload/download
│       └── monitoring.py   # Health checks
├── 📁 tests/               # Test suite
│   ├── conftest.py         # Test fixtures & setup
│   ├── test_auth.py        # Authentication tests
│   └── test_tasks.py       # Task endpoint tests
├── 📁 alembic/             # Database migrations
│   └── versions/           # Migration scripts
├── 📁 scripts/             # Utility scripts
│   ├── backup.sh           # Database backup
│   └── deploy.sh           # Deployment automation
├── docker-compose.yml      # Local development setup
├── docker-compose.prod.yml # Production configuration
├── Dockerfile              # Container definition
├── pyproject.toml          # Poetry dependencies
└── alembic.ini             # Alembic configuration
```

### 📂 Key Directories Explained

#### **`src/app/core/`** - Application Core
Contains all cross-cutting concerns and shared utilities:
- **`config.py`**: Centralized configuration using Pydantic Settings (environment variables, database URL, JWT secrets)
- **`cache.py`**: Redis connection manager with error handling & graceful degradation
- **`rate_limiter.py`**: Fixed-window rate limiting using Redis counters
- **`decorators.py`**: Custom `@cached` decorator for automatic function result caching

#### **`src/app/crud/`** - Repository Pattern
Implements the repository pattern for data access:
- **`base.py`**: Generic CRUD base class with type safety (TypeVar for models)
- Specific implementations extend the base with custom query methods
- All database operations are async for performance

#### **`src/app/routers/`** - API Layer
RESTful endpoints organized by domain:
- Dependency injection for database sessions & authentication
- Pydantic models for request/response validation
- Rate limiting applied per endpoint

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL 15+
- Redis 7+
- Docker (optional but recommended)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/govindKulk/fastapi-practice.git
cd fastapi-practice

# Start all services (FastAPI + PostgreSQL + Redis)
docker-compose up -d

# Run migrations
docker-compose exec web alembic upgrade head

# API is now available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Option 2: Local Setup

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Create .env file (copy from .env.example)
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://myuser:password@localhost/mydb
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-change-this-in-production
EOF

# Start PostgreSQL and Redis (via Docker or local)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
docker run -d -p 6379:6379 redis:7-alpine

# Run migrations
poetry run alembic upgrade head

# Start the development server
poetry run uvicorn src.app.main:task_app --reload --host 0.0.0.0 --port 8000
```

### 🎯 Quick Test

```bash
# Register a user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# Login to get JWT token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# Use the token to create a task
curl -X POST "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Task", "description": "Task description", "priority": "high"}'
```

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login (JSON) | ❌ |
| POST | `/auth/login/access-token` | OAuth2 login (form) | ❌ |

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tasks/` | List tasks (paginated, filtered) | ✅ |
| POST | `/tasks/` | Create task | ✅ |
| GET | `/tasks/{id}` | Get task by ID | ✅ |
| PUT | `/tasks/{id}` | Update task | ✅ |
| DELETE | `/tasks/{id}` | Delete task | ✅ |
| GET | `/tasks/statistics` | Task statistics | ✅ |

**Query Parameters for `/tasks/`:**
- `skip`: Number of records to skip (pagination)
- `limit`: Max records to return (1-100)
- `priority`: Filter by priority (low, medium, high)
- `status`: Filter by status (pending, in_progress, completed)
- `search`: Search in title/description

### Files

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/upload` | Upload file (max 5MB) | ✅ |
| GET | `/download/{filename}` | Download file | ✅ |
| DELETE | `/delete/{filename}` | Delete file | ✅ |

### Monitoring

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/monitoring/health` | Health check | ❌ |
| GET | `/monitoring/metrics` | App metrics | ❌ |

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎨 Design Patterns & Principles

### 1️⃣ **Repository Pattern** (CRUD Layer)

```python
# Generic base repository with type safety
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        # Generic get implementation
```

**Why?**
- Abstracts database operations from business logic
- Provides consistent interface for all models
- Easy to test with mock repositories
- Type-safe operations with generics

### 2️⃣ **Dependency Injection** (FastAPI Dependencies)

```python
# Database session injection
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Current user extraction
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    # Validate token and return user
```

**Why?**
- Loose coupling between components
- Easy to swap implementations (testing, different databases)
- Automatic cleanup (context managers)
- Built into FastAPI's design

### 3️⃣ **Decorator Pattern** (Custom Caching)

```python
@cached(ttl=300, key_prefix="tasks_by_owner")
async def get_tasks_by_owner_cached(
    db: AsyncSession,
    owner_id: int,
    skip: int = 0,
    limit: int = 10,
    ...
) -> tuple[List[TaskResponse], int]:
    # Function result automatically cached in Redis
```

**Why?**
- Non-invasive caching (function remains clean)
- Configurable TTL and key generation
- Automatic serialization/deserialization
- Graceful degradation if Redis is down

### 4️⃣ **Settings Pattern** (Pydantic Settings)

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()  # Auto-loads from .env
```

**Why?**
- Type-safe configuration
- Environment-based deployment (dev/staging/prod)
- Validation at startup (fail fast)
- Single source of truth

### 5️⃣ **Manager Pattern** (Cache & Rate Limiter)

```python
class CacheManager:
    async def connect(self): ...
    async def get(self, key: str): ...
    async def set(self, key: str, value: Any, ttl: int): ...

cache_manager = CacheManager(settings.REDIS_URL)
```

**Why?**
- Encapsulates complex initialization logic
- Singleton-like behavior for shared resources
- Graceful error handling
- Lifecycle management (startup/shutdown)

### 6️⃣ **Middleware Pattern** (Request Processing)

```python
@task_app.middleware("http")
async def fun_middleware(request, call_next):
    # Log every request with random emoji
    logger.info(f"🚀 Processing request...")
    response = await call_next(request)
    return response
```

**Why?**
- Cross-cutting concerns (logging, timing, CORS)
- Request/response transformation
- Centralized error handling
- Doesn't clutter endpoint code

---

## 🔍 Key Implementation Details

### 🔐 JWT Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database
    participant JWT

    Client->>API: POST /auth/login (username, password)
    API->>Database: Query user by username
    Database-->>API: User data (hashed password)
    API->>API: Verify password (bcrypt)
    API->>JWT: Create access token (HS256)
    JWT-->>API: Signed JWT token
    API-->>Client: {access_token, token_type}
    
    Client->>API: GET /tasks/ (Authorization: Bearer TOKEN)
    API->>JWT: Decode & verify token
    JWT-->>API: Username from token
    API->>Database: Get user by username
    Database-->>API: User object
    API->>API: Process request with user context
    API-->>Client: Response data
```

**Implementation Highlights:**
- **Password Hashing**: bcrypt with automatic salt generation
- **Token Expiry**: Configurable (default 7 days)
- **OAuth2 Compatibility**: Supports both JSON and form-based login
- **Dependency Chain**: `oauth2_scheme` → `get_current_user` → `get_current_active_user`

### ⚡ Redis Caching Strategy

**Cache Key Generation:**
```python
# Automatic key from function name + arguments
key = f"tasks_by_owner:{owner_id}:{skip}:{limit}:{priority}:{status}:{search}"
```

**Cache Invalidation:**
```python
# When task is created/updated/deleted
await cache_manager.clear_pattern(f"tasks_by_owner:*:{user_id}:*")
```

**Graceful Degradation:**
- If Redis is unavailable, app continues without caching
- Logs warnings but doesn't crash
- Functions execute normally (just slower)

### 🚦 Rate Limiting Algorithm

**Fixed Window Counter:**
```python
# Window aligned to clock time
window_start = (current_time // window_seconds) * window_seconds
key = f"rate_limit:{ip_address}:{window_start}"

# Increment counter in Redis with TTL
count = redis.incr(key)
redis.expire(key, window_seconds)

if count > max_requests:
    raise HTTPException(429, "Rate limit exceeded")
```

**Rate Tiers:**
- **Strict**: 10 requests/minute (write operations)
- **Moderate**: 60 requests/minute (read operations)

### 📊 Database Schema

**User Table:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Task Table:**
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high
    status VARCHAR(20) DEFAULT 'pending',   -- pending, in_progress, completed
    due_date TIMESTAMP,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_owner_id ON tasks(owner_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

---

## 🧪 Testing

### Test Structure

```bash
tests/
├── conftest.py           # Fixtures (test DB, client, auth)
├── test_auth.py          # Authentication tests
├── test_tasks.py         # Task CRUD tests
└── core/
    └── test_math_operations.py  # Utility tests
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Specific test file
poetry run pytest tests/test_auth.py

# Verbose output
poetry run pytest -v -s
```

### Test Highlights

**In-Memory SQLite for Testing:**
```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```
- Fast test execution
- No need for test database setup
- Isolated test runs

**Fixtures for Authentication:**
```python
@pytest_asyncio.fixture
async def authenticated_client(client, db):
    # Creates user and returns client with auth headers
```

**Coverage:** Comprehensive tests for all endpoints with edge cases

---

## 🐳 Docker Deployment

### Development Environment

```bash
docker-compose up -d
```

**Services:**
- `web`: FastAPI app (port 8000)
- `db`: PostgreSQL 15 (port 5432)
- `redis`: Redis 7 (port 6379)

### Production Environment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Production Differences:**
- No volume mounts for code (baked into image)
- Optimized settings (no reload, production logging)
- Health checks configured
- Resource limits set

### Dockerfile Optimization

```dockerfile
FROM python:3.13-slim

# Install dependencies first (cached layer)
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

# Copy application code
COPY . .

# Run as non-root user
USER nobody

CMD ["uvicorn", "src.app.main:task_app", "--host", "0.0.0.0"]
```

---

## 📚 Additional Notes

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-min-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# CORS (optional)
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

### Performance Tips

1. **Database Indexes**: Added on frequently queried columns (`owner_id`, `status`, `priority`)
2. **Connection Pooling**: SQLAlchemy manages connection pool automatically
3. **Async Operations**: All I/O operations use async/await
4. **Redis Caching**: Reduces database load for read-heavy operations
5. **Pagination**: Prevents large result sets from overwhelming memory

---

## 📫 Contact

**Developer**: Govind Kulkarni  
**Email**: kulkarnigovind2003@gmail.com  
**GitHub**: [@govindKulk](https://github.com/govindKulk)  
**Repository**: [fastapi-practice](https://github.com/govindKulk/fastapi-practice)

---

---

<div align="center">

**Built with ❤️ using FastAPI**

⭐ Star this repo if you found it helpful!

</div>
