"""
    Database configuration and connection setup.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings


# Engine : Engine is used to manage the connection pool to the database.
engine = create_async_engine(url=settings.DATABASE_URL, echo=True)

# Session Local : This is a factory for creating new AsyncSession instances.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency to get DB session (to be used in FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:

    # Uses context manager to ensure session is properly closed after use
    async with AsyncSessionLocal() as session:
        # this sytnax allows yielding the session for use in routes
        yield session

# Base class for declarative models
# Used by ORM models to inherit from.
Base = declarative_base()