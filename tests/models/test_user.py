from sqlalchemy import select

from app.models.user import Users


class TestUser:
    async def test_user_creation(self, db_session):
        user = Users(
            username="testuser",
            email="testuser@test.local",
            password="testpassword",
            name="Test User",
            role="USER",
        )
        db_session.add(user)
        await db_session.commit()
        assert user.id == 2
        assert user.username == "testuser"
        assert user.email == "testuser@test.local"
        print(f"user.password: {user.password}")
        assert user.name == "Test User"
        assert user.role == "USER"

        system_user = select(Users)
        system_user = (await db_session.execute(system_user)).scalars()
        print(f"system_user: {system_user}")
        system_user = system_user[0]
        assert system_user.id == 1
        assert system_user.username == "system"
        assert system_user.email == "system@test.local"
        print(f"system_user.password: {system_user.password}")
        assert system_user.name == "System User"
        assert system_user.role == "SYSTEM"
