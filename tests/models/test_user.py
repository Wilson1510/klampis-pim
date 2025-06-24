from sqlalchemy import String, event, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from app.models.user import Users
from app.core.listeners import hash_new_password_listener
from app.core.security import verify_password
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
)


class TestUser:
    """Test suite for User model"""
    @pytest.fixture(autouse=True)
    async def setup_objects(self, db_session: AsyncSession):
        """Setup method for the test suite"""
        # Create a user
        self.test_user1 = Users(
            username="testuser",
            email="testuser@test.local",
            name="Test User",
            password="testpassword",
            role="USER",
            created_by=1,
            updated_by=1
        )
        await save_object(db_session, self.test_user1)

        # Create a user with a different role
        self.test_user2 = Users(
            username="testuser2",
            email="testuser2@test.local",
            name="Test User 2",
            password="testpassword2",
            role="ADMIN",
            created_by=1,
            updated_by=1
        )
        await save_object(db_session, self.test_user2)

    def test_inheritance_from_base_model(self):
        """Test that the User model inherits from the Base model"""
        assert issubclass(Users, Base)

    def test_fields_with_validation(self):
        """Test that the model has the expected validation"""
        assert hasattr(Users, 'validate_email')
        assert hasattr(Users, 'validate_role')
        assert not hasattr(Users, 'validate_last_login')
        assert not hasattr(Users, 'validate_created_by')

        assert 'email' in Users.__mapper__.validators
        assert 'role' in Users.__mapper__.validators
        assert len(Users.__mapper__.validators) == 2
        assert 'last_login' not in Users.__mapper__.validators
        assert 'created_by' not in Users.__mapper__.validators

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(Users, 'before_insert', hash_new_password_listener)
        assert event.contains(Users, 'before_update', hash_new_password_listener)
        assert not event.contains(Users, 'after_insert', hash_new_password_listener)

    def test_username_field_properties(self):
        """Test the properties of the username field"""
        username_column = Users.__table__.columns.get('username')
        assert username_column is not None
        assert isinstance(username_column.type, String)
        assert username_column.type.length == 20
        assert username_column.nullable is False
        assert username_column.unique is True
        assert username_column.index is True
        assert username_column.default is None

    def test_name_field_properties(self):
        """Test the properties of the name field"""
        name_column = Users.__table__.columns.get('name')
        assert name_column is not None
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 50
        assert name_column.nullable is False
        assert name_column.unique is None
        assert name_column.index is None
        assert name_column.default is None

    def test_email_field_properties(self):
        """Test the properties of the email field"""
        email_column = Users.__table__.columns.get('email')
        assert email_column is not None
        assert isinstance(email_column.type, String)
        assert email_column.type.length == 100
        assert email_column.nullable is False
        assert email_column.unique is True
        assert email_column.index is True
        assert email_column.default is None

    def test_password_field_properties(self):
        """Test the properties of the password field"""
        password_column = Users.__table__.columns.get('password')
        assert password_column is not None
        assert isinstance(password_column.type, String)
        assert password_column.type.length == 255
        assert password_column.nullable is False
        assert password_column.unique is None
        assert password_column.index is None
        assert password_column.default is None

    def test_role_field_properties(self):
        """Test the properties of the role field"""
        role_column = Users.__table__.columns.get('role')
        assert role_column is not None
        assert isinstance(role_column.type, String)
        assert role_column.type.length is None
        assert role_column.nullable is False
        assert role_column.unique is None
        assert role_column.index is None
        assert role_column.default.arg == "USER"

    def test_last_login_field_properties(self):
        """Test the properties of the last_login field"""
        last_login_column = Users.__table__.columns.get('last_login')
        assert last_login_column is not None
        assert isinstance(last_login_column.type, DateTime)
        assert last_login_column.nullable is True
        assert last_login_column.unique is None
        assert last_login_column.index is None
        assert last_login_column.default is None

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_user1)

        # Should follow the pattern: Users(username=<username>)
        assert str_repr == "Users(username=testuser, name=Test User)"

    def test_init_method(self):
        """Test the init method"""
        # Refresh the test_user1 with the created_by and updated_by relationship
        assert self.test_user1.id == 2
        assert self.test_user1.username == "testuser"
        assert self.test_user1.email == "testuser@test.local"
        assert self.test_user1.name == "Test User"
        assert verify_password("testpassword", self.test_user1.password)
        assert self.test_user1.role == "USER"
        assert self.test_user1.last_login is None

        assert self.test_user2.id == 3
        assert self.test_user2.username == "testuser2"
        assert self.test_user2.email == "testuser2@test.local"
        assert self.test_user2.name == "Test User 2"
        assert verify_password("testpassword2", self.test_user2.password)
        assert self.test_user2.role == "ADMIN"
        assert self.test_user2.last_login is None

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = Users(
            username="testuser3",
            email="testuser3@test.local",
            name="Test User 3",
            password="testpassword3",
            role="USER"
        )
        await save_object(db_session, item)

        assert item.id == 4
        assert item.username == "testuser3"
        assert item.email == "testuser3@test.local"
        assert item.name == "Test User 3"
        assert verify_password("testpassword3", item.password)
        assert item.role == "USER"
        assert item.last_login is None

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(db_session, Users, self.test_user1.id)
        assert item.id == 2
        assert item.username == "testuser"
        assert item.email == "testuser@test.local"
        assert item.name == "Test User"
        assert verify_password("testpassword", item.password)
        assert item.role == "USER"
        assert item.last_login is None

        item = await get_object_by_id(db_session, Users, self.test_user2.id)
        assert item.id == 3
        assert item.username == "testuser2"
        assert item.email == "testuser2@test.local"
        assert item.name == "Test User 2"
        assert verify_password("testpassword2", item.password)
        assert item.role == "ADMIN"
        assert item.last_login is None

        item = await get_all_objects(db_session, Users)
        assert len(item) == 3

        assert item[0].id == 1
        assert item[0].username == "system"
        assert item[0].email == "system@test.local"
        assert item[0].name == "System User"
        assert verify_password("systempassword", item[0].password)
        assert item[0].role == "SYSTEM"
        assert item[0].last_login is None
        assert item[0].created_by is None
        assert item[0].updated_by is None

        assert item[1].id == 2
        assert item[1].username == "testuser"
        assert item[1].email == "testuser@test.local"
        assert item[1].name == "Test User"
        assert verify_password("testpassword", item[1].password)
        assert item[1].role == "USER"
        assert item[1].last_login is None

        assert item[2].id == 3
        assert item[2].username == "testuser2"
        assert item[2].email == "testuser2@test.local"
        assert item[2].name == "Test User 2"
        assert verify_password("testpassword2", item[2].password)
        assert item[2].role == "ADMIN"
        assert item[2].last_login is None

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(db_session, Users, self.test_user1.id)
        item.name = "Updated Test User"
        item.role = "ADMIN"
        await save_object(db_session, item)

        assert item.id == 2
        assert item.username == "testuser"
        assert item.email == "testuser@test.local"
        assert item.name == "Updated Test User"
        assert verify_password("testpassword", item.password)
        assert item.role == "ADMIN"
        assert item.last_login is None

        item.username = "updatedtestuser"
        item.email = "updated_testuser@test.local"
        await save_object(db_session, item)

        assert item.id == 2
        assert item.username == "updatedtestuser"
        assert item.email == "updated_testuser@test.local"
        assert item.name == "Updated Test User"
        assert verify_password("testpassword", item.password)
        assert item.role == "ADMIN"
        assert item.last_login is None

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_user1)

        item = await get_object_by_id(db_session, Users, self.test_user1.id)
        assert item is None

        item = await get_all_objects(db_session, Users)
        assert len(item) == 2
