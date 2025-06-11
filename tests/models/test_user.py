from sqlalchemy import select

from app.models.user import Users
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    update_object,
    delete_object,
)


class TestUser:
    async def test_user_creation(self, db_session):
        user = Users(
            username="testuser",
            email="testuser@test.local",
            password="testpassword",
            name="Test User",
            role="USER",
        )
        await save_object(db_session, user)
        user = await get_object_by_id(db_session, Users, user.id)
        print(f"user: {user}")
        assert user.id == 2
        assert user.username == "testuser"
        assert user.email == "testuser@test.local"
        assert user.name == "Test User"
        assert user.role == "USER"



