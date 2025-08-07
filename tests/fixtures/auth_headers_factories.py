import pytest
from app.core.security import create_access_token
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Users


@pytest.fixture
async def auth_headers_system():
    """Create authentication headers with JWT token."""
    token = create_access_token(subject=settings.SYSTEM_USER_ID)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_headers_admin(db_session: AsyncSession):
    """Create authentication headers with JWT token."""
    admin_user = Users(
        username="admin",
        email="admin@test.com",
        password="adminpassword",
        name="Admin User",
        role="ADMIN",
        sequence=2
    )
    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)
    token = create_access_token(subject=settings.ADMIN_USER_ID)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_headers_user(db_session: AsyncSession):
    """Create authentication headers with JWT token."""
    user_user = Users(
        username="user",
        email="user@test.com",
        password="userpassword",
        name="User User",
        role="USER",
        sequence=3
    )
    db_session.add(user_user)
    await db_session.commit()
    await db_session.refresh(user_user)
    token = create_access_token(subject=user_user.id)
    return {"Authorization": f"Bearer {token}"}
