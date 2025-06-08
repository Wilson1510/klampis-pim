from unittest.mock import patch

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import pytest

from app.core.session import engine, async_session_factory, get_db


class TestSessionModule:
    """Test cases for the session module."""

    def test_engine_creation(self):
        """Test that the engine is created with correct configuration."""
        # Verify engine is created
        assert engine is not None

        # Verify engine URL contains the expected components
        # Note: SQLAlchemy masks passwords in URL string representation
        engine_url_str = str(engine.url)
        assert "postgresql+asyncpg://" in engine_url_str
        assert "@localhost:5432/klampis_pim" in engine_url_str

        # Verify engine configuration
        assert engine.echo is False

    def test_async_session_factory_creation(self):
        """Test that the async session factory is created correctly."""
        # Verify session factory is created
        assert async_session_factory is not None

        # Verify it's a sessionmaker instance
        assert isinstance(async_session_factory, sessionmaker)

        # Verify configuration - access via kw dict for sessionmaker
        assert async_session_factory.kw.get('expire_on_commit') is False
        # Compare class name instead of class object due to different import paths
        assert async_session_factory.class_.__name__ == "AsyncSession"

    async def test_get_db_yields_session(self):
        """Test that get_db yields a valid AsyncSession."""
        session_generator = get_db()

        # Get the session from the generator
        session = await session_generator.__anext__()

        # Verify it's an AsyncSession instance
        assert isinstance(session, AsyncSession)

        # Verify session is not closed initially
        assert session.is_active is not False  # Session should be active

        # Clean up - close the session
        await session.close()

    async def test_get_db_session_lifecycle(self):
        """Test the complete lifecycle of get_db session."""
        session_generator = get_db()
        # Get the session
        session = await session_generator.__anext__()

        # Verify session is active
        assert isinstance(session, AsyncSession)

        # Simulate some database operation (without actual DB call)
        # This tests that the session can be used
        assert session.bind is not None
        # Clean up

        await session_generator.aclose()

    async def test_get_db_context_manager_behavior(self):
        """Test that get_db properly manages session context."""
        sessions_created = []

        # Mock the session factory to track session creation
        original_factory = async_session_factory

        def mock_session_factory():
            session = original_factory()
            sessions_created.append(session)
            return session

        patch_target = 'app.core.session.async_session_factory'
        with patch(patch_target, side_effect=mock_session_factory):
            async for session in get_db():
                # Verify we got a session
                assert isinstance(session, AsyncSession)
                # Break after first iteration to simulate normal usage
                break

        # Verify session was created
        assert len(sessions_created) >= 1

    @patch('app.core.session.async_session_factory')
    async def test_get_db_handles_session_creation_error(self, mock_factory):
        """Test that get_db handles session creation errors gracefully."""
        # Mock session factory to raise an exception
        mock_factory.side_effect = SQLAlchemyError("Database connection failed")

        # Test that the error is propagated
        with pytest.raises(SQLAlchemyError, match="Database connection failed"):
            async for session in get_db():
                pass

    def test_engine_configuration_with_different_database_uri(self):
        """Test engine creation with different database URI configurations."""
        # Test with different URI format
        test_uri = "postgresql+asyncpg://test:test@localhost:5432/test_db"

        with patch('app.core.config.settings') as mock_settings:
            mock_settings.DATABASE_URI = test_uri

            # Re-import to get new engine with mocked settings
            from importlib import reload
            import app.core.session
            reloaded_session = reload(app.core.session)

            # Verify new engine uses the test URI components
            engine_url_str = str(reloaded_session.engine.url)
            assert "postgresql+asyncpg://" in engine_url_str
            assert "@localhost:5432/test_db" in engine_url_str

    async def test_multiple_concurrent_sessions(self):
        """Test that multiple concurrent sessions can be created."""
        sessions = []

        # Create multiple sessions concurrently
        for _ in range(3):
            session_gen = get_db()
            session = await session_gen.__anext__()
            sessions.append((session_gen, session))

        # Verify all sessions are different instances
        session_objects = [s[1] for s in sessions]
        assert len(set(id(s) for s in session_objects)) == 3

        # Clean up all sessions
        for session_gen, session in sessions:
            await session.close()
            await session_gen.aclose()

    def test_session_factory_configuration_parameters(self):
        """Test that session factory has correct configuration parameters."""
        # Verify expire_on_commit is False (important for async operations)
        assert async_session_factory.kw.get('expire_on_commit') is False

        # Compare class name instead of class object due to different import paths
        assert async_session_factory.class_.__name__ == "AsyncSession"

        # Verify bind is the engine (stored in kw dict)
        assert async_session_factory.kw.get('bind') == engine

    async def test_get_db_docstring_and_type_hints(self):
        """Test that get_db has proper documentation and type hints."""
        # Verify function has docstring
        assert get_db.__doc__ is not None
        assert "Dependency for getting async database session" in get_db.__doc__

        # Verify return type annotation
        import inspect
        signature = inspect.signature(get_db)
        return_annotation = signature.return_annotation

        # The return type should be AsyncSession (from the generator)
        assert return_annotation == AsyncSession

    async def test_session_transaction_behavior(self):
        """Test session transaction behavior in get_db."""
        async for session in get_db():
            # Verify session can handle transactions
            assert hasattr(session, 'begin')
            assert hasattr(session, 'commit')
            assert hasattr(session, 'rollback')

            # Test that session is not in a transaction initially
            assert not session.in_transaction()
            break

    async def test_session_database_connectivity(self, db_session):
        """Test that session can connect to database using test fixtures."""
        # This test uses the db_session fixture from conftest.py
        # to verify integration with the test database setup

        # Verify session is an AsyncSession
        assert isinstance(db_session, AsyncSession)

        # Verify session is active
        assert db_session.is_active is not False

        # Test basic database operation using text() for raw SQL
        result = await db_session.execute(text("SELECT 1 as test_value"))
        row = result.fetchone()
        assert row[0] == 1
