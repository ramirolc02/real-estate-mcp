"""Pytest fixtures for testing."""

import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.property import Base, Property

# Use SQLite for testing (in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Configure SQLite for testing
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    """Enable foreign keys and configure SQLite for testing."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def sample_property(test_session: AsyncSession) -> Property:
    """Create a sample property for testing."""
    prop = Property(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        title="Test Property",
        description="A test property for unit tests",
        city="Lisbon",
        address="Test Street 123",
        price=500000,
        status="available",
        property_type="apartment",
        bedrooms=2,
        bathrooms=1,
        area_sqm=80.0,
        features=["balcony", "parking"],
        internal_notes="Test notes",
    )
    test_session.add(prop)
    await test_session.commit()
    await test_session.refresh(prop)
    return prop
