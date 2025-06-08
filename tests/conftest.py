import pytest
import psycopg2
import asyncio
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

# Import the SQLAlchemy components from your project
from app.core.base import Base
from app.models.user import Users  # Required for foreign key constraints in Base model
from app.core.session import get_db
from httpx import AsyncClient
from app.main import app
from httpx import ASGITransport
# Constants for database connection
TEST_DB_NAME = "test_db"


@pytest.fixture(scope="session")
def create_test_database():
    """
    Session-scoped fixture that creates a test database at the beginning
    of the test session and drops it after all tests are complete.
    """
    # Parse admin connection parameters from the URL
    admin_params = settings.ADMIN_PARAMS

    # Create a connection to the admin database
    conn = psycopg2.connect(**admin_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    try:
        # Check if the test database already exists
        cursor.execute(
            f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'"
        )
        exists = cursor.fetchone()

        # If it exists, drop it first
        if exists:
            cursor.execute(f"DROP DATABASE {TEST_DB_NAME}")

        # Create the test database
        cursor.execute(f"CREATE DATABASE {TEST_DB_NAME}")
        print(f"Created test database: {TEST_DB_NAME}")

        yield  # This is where the testing happens

    except Exception as e:
        print(f"Error during test database creation: {e}")
        raise
    finally:
        # Close the admin database connection
        cursor.close()
        conn.close()

        # After tests are done, reconnect and drop the test database
        try:
            conn = psycopg2.connect(**admin_params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Terminate any existing connections to the test database
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{TEST_DB_NAME}'
                AND pid <> pg_backend_pid()
            """)

            # Drop the test database
            cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
            print(f"Dropped test database: {TEST_DB_NAME}")

        except Exception as e:
            print(f"Error during test database cleanup: {e}")
        finally:
            cursor.close()
            conn.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine(create_test_database):
    """Create and yield the engine, then dispose of it after tests."""
    engine = create_async_engine(
        settings.DATABASE_URI.replace("klampis_pim", TEST_DB_NAME), echo=False
    )

    # Create all tables
    async with engine.begin() as conn:
        # Ensure Users model is registered for foreign key constraints
        _ = Users  # noqa: F841
        await conn.run_sync(Base.metadata.create_all)

    # Create system user after tables are created
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # Create system user if it doesn't exist
        system_user = Users(
            id=settings.SYSTEM_USER_ID,
            username="system",
            password="systempassword",
            name="System User",
            role="SYSTEM",
            created_by=None,  # System user creates itself
            updated_by=None,
            sequence=1
        )
        session.add(system_user)
        await session.commit()

    yield engine

    # Drop all tables and dispose of the engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Function-scoped fixture that provides a database session."""
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
async def async_client(db_session) -> AsyncGenerator:
    """
    Function-scoped fixture that provides an async test client
    with a database session dependency for FastAPI testing.
    """

    # Override the get_db dependency to use our test db_session
    async def override_get_db():
        yield db_session

    # Apply the override
    app.dependency_overrides[get_db] = override_get_db

    # Create a client using ASGITransport for newer httpx versions
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    # Reset the override after the test
    app.dependency_overrides = {}
