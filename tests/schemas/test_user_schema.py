from typing import Optional, Literal
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import StrictStr, EmailStr
from pydantic_core import PydanticUndefined
import pytest

from app.schemas.base import BaseSchema, BaseCreateSchema, BaseUpdateSchema, BaseInDB
from app.schemas.user_schema import (
    UserBase, UserCreate, UserUpdate, UserResponse,
    UserLogin, UserChangePassword, Token, TokenRefresh
)
from app.models.user_model import Users
from tests.utils.model_test_utils import save_object


class TestUserBase:
    """Test cases for the user base schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.user_dict = {
            "username": "testuser",
            "email": "test@example.com",
            "name": "Test User",
            "role": "USER"
        }

    def test_user_base_schema_inheritance(self):
        """Test that the user base schema inherits from BaseSchema"""
        assert issubclass(UserBase, BaseSchema)

    def test_user_base_fields_inheritance(self):
        """Test that the user base schema has correct fields"""
        fields = UserBase.model_fields
        assert len(fields) == 4
        assert 'username' in fields
        assert 'email' in fields
        assert 'name' in fields
        assert 'role' in fields

        username = fields['username']
        assert username.is_required() is True
        assert username.annotation == str
        assert username.default is PydanticUndefined
        assert username.metadata[0].min_length == 3
        assert username.metadata[1].max_length == 20
        assert username.metadata[2].strict is True

        email = fields['email']
        assert email.is_required() is True
        assert email.annotation == EmailStr
        assert email.default is PydanticUndefined
        assert email.metadata[0].min_length == 1
        assert email.metadata[1].max_length == 50

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        role = fields['role']
        assert role.is_required() is False
        assert role.annotation == Literal["USER", "ADMIN", "SYSTEM", "MANAGER"]
        assert role.default == "USER"

    def test_user_base_schema_input(self):
        schema = UserBase(**self.user_dict)
        assert schema.username == "testuser"
        assert schema.email == "test@example.com"
        assert schema.name == "Test User"
        assert schema.role == "USER"

    def test_user_base_schema_input_updated(self):
        schema = UserBase(**self.user_dict)
        assert schema.username == "testuser"
        assert schema.email == "test@example.com"
        assert schema.name == "Test User"
        assert schema.role == "USER"

        schema.username = "updateduser"
        schema.name = "Updated User"
        assert schema.username == "updateduser"
        assert schema.name == "Updated User"

    def test_user_base_schema_model_dump(self):
        schema = UserBase(**self.user_dict)
        assert schema.model_dump() == {
            "username": "testuser",
            "email": "test@example.com",
            "name": "Test User",
            "role": "USER"
        }

    def test_user_base_schema_model_dump_json(self):
        schema = UserBase(**self.user_dict)
        assert schema.model_dump_json() == '{'\
            '"username":"testuser",'\
            '"email":"test@example.com",'\
            '"name":"Test User",'\
            '"role":"USER"'\
            '}'


class TestUserCreate:
    """Test cases for the user create schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.user_dict = {
            "username": "testuser",
            "email": "test@example.com",
            "name": "Test User",
            "role": "USER",
            "password": "password123"
        }

    def test_user_create_schema_inheritance(self):
        """Test that the user create schema inherits from UserBase"""
        assert issubclass(UserCreate, UserBase)
        assert issubclass(UserCreate, BaseCreateSchema)

    def test_user_create_fields_inheritance(self):
        """Test that the user create schema has correct fields"""
        fields = UserCreate.model_fields
        assert len(fields) == 9  # 4 base + 5 from BaseCreateSchema
        assert 'username' in fields
        assert 'email' in fields
        assert 'name' in fields
        assert 'role' in fields
        assert 'password' in fields

        username = fields['username']
        assert username.is_required() is True
        assert username.annotation == str
        assert username.default is PydanticUndefined
        assert username.metadata[0].min_length == 3
        assert username.metadata[1].max_length == 20
        assert username.metadata[2].strict is True

        email = fields['email']
        assert email.is_required() is True
        assert email.annotation == EmailStr
        assert email.default is PydanticUndefined
        assert email.metadata[0].min_length == 1
        assert email.metadata[1].max_length == 50

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        role = fields['role']
        assert role.is_required() is False
        assert role.annotation == Literal["USER", "ADMIN", "SYSTEM", "MANAGER"]
        assert role.default == "USER"

        password = fields['password']
        assert password.is_required() is True
        assert password.annotation == str
        assert password.default is PydanticUndefined
        assert password.metadata[0].min_length == 6
        assert password.metadata[1].strict is True

    def test_user_create_schema_input(self):
        schema = UserCreate(**self.user_dict)
        assert schema.username == "testuser"
        assert schema.email == "test@example.com"
        assert schema.name == "Test User"
        assert schema.role == "USER"
        assert schema.password == "password123"

    def test_user_create_schema_input_updated(self):
        schema = UserCreate(**self.user_dict)
        assert schema.password == "password123"

        schema.password = "newpassword456"
        assert schema.password == "newpassword456"

    def test_user_create_schema_model_dump(self):
        schema = UserCreate(**self.user_dict)
        assert schema.model_dump() == {
            "is_active": True,
            "sequence": 0,
            "created_by": 1,
            "updated_by": 1,
            "username": "testuser",
            "email": "test@example.com",
            "name": "Test User",
            "role": "USER",
            "password": "password123"
        }

    def test_user_create_schema_model_dump_json(self):
        schema = UserCreate(**self.user_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":true,'\
            '"sequence":0,'\
            '"created_by":1,'\
            '"updated_by":1,'\
            '"username":"testuser",'\
            '"email":"test@example.com",'\
            '"name":"Test User",'\
            '"role":"USER",'\
            '"password":"password123"'\
            '}'


class TestUserUpdate:
    """Test cases for the user update schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.user_dict = {
            "username": "updateduser",
            "email": "updated@example.com",
            "name": "Updated User",
            "role": "ADMIN",
            "is_active": False
        }

    def test_user_update_schema_inheritance(self):
        """Test that the user update schema inherits from UserBase"""
        assert issubclass(UserUpdate, UserBase)
        assert issubclass(UserUpdate, BaseUpdateSchema)

    def test_user_update_fields_inheritance(self):
        """Test that the user update schema has correct fields"""
        fields = UserUpdate.model_fields
        assert len(fields) == 7  # 4 base + 3 from BaseUpdateSchema
        assert 'username' in fields
        assert 'email' in fields
        assert 'name' in fields
        assert 'role' in fields

        username = fields['username']
        assert username.is_required() is False
        assert username.annotation == Optional[StrictStr]
        assert username.default is None
        assert username.metadata[0].min_length == 3
        assert username.metadata[1].max_length == 20

        email = fields['email']
        assert email.is_required() is False
        assert email.annotation == Optional[EmailStr]
        assert email.default is None
        assert email.metadata[0].min_length == 1
        assert email.metadata[1].max_length == 50

        name = fields['name']
        assert name.is_required() is False
        assert name.annotation == Optional[StrictStr]
        assert name.default is None
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50

        role = fields['role']
        assert role.is_required() is False
        assert role.annotation == Optional[
            Literal["USER", "ADMIN", "SYSTEM", "MANAGER"]
        ]
        assert role.default is None

    def test_user_update_schema_input(self):
        schema = UserUpdate(**self.user_dict)
        assert schema.username == "updateduser"
        assert schema.email == "updated@example.com"
        assert schema.name == "Updated User"
        assert schema.role == "ADMIN"
        assert schema.is_active is False

    def test_user_update_schema_input_partial(self):
        """Test user update with partial data"""
        partial_dict = {"username": "partialuser"}
        schema = UserUpdate(**partial_dict)
        assert schema.username == "partialuser"
        assert schema.email is None
        assert schema.name is None
        assert schema.role is None
        assert schema.is_active is None

    def test_user_update_schema_input_empty(self):
        """Test user update with empty data"""
        schema = UserUpdate()
        assert schema.username is None
        assert schema.email is None
        assert schema.name is None
        assert schema.role is None
        assert schema.is_active is None

    def test_user_update_schema_model_dump(self):
        schema = UserUpdate(**self.user_dict)
        assert schema.model_dump() == {
            "is_active": False,
            "sequence": None,
            "updated_by": None,
            "username": "updateduser",
            "email": "updated@example.com",
            "name": "Updated User",
            "role": "ADMIN"
        }

    def test_user_update_schema_model_dump_json(self):
        schema = UserUpdate(**self.user_dict)
        assert schema.model_dump_json() == '{'\
            '"is_active":false,'\
            '"sequence":null,'\
            '"updated_by":null,'\
            '"username":"updateduser",'\
            '"email":"updated@example.com",'\
            '"name":"Updated User",'\
            '"role":"ADMIN"'\
            '}'


class TestUserResponse:
    """Test cases for the user response schema"""

    def test_user_response_schema_inheritance(self):
        """Test that the user response schema inherits from UserBase"""
        assert issubclass(UserResponse, UserBase)
        assert issubclass(UserResponse, BaseInDB)

    def test_user_response_fields_inheritance(self):
        """Test that the user response schema has correct fields"""
        fields = UserResponse.model_fields
        assert len(fields) == 12
        assert 'username' in fields
        assert 'email' in fields
        assert 'name' in fields
        assert 'role' in fields
        assert 'last_login' in fields
        assert 'created_by' in fields
        assert 'updated_by' in fields

        username = fields['username']
        assert username.is_required() is True
        assert username.annotation == str
        assert username.default is PydanticUndefined
        assert username.metadata[0].min_length == 3
        assert username.metadata[1].max_length == 20
        assert username.metadata[2].strict is True

        email = fields['email']
        assert email.is_required() is True
        assert email.annotation == EmailStr
        assert email.default is PydanticUndefined
        assert email.metadata[0].min_length == 1
        assert email.metadata[1].max_length == 50

        name = fields['name']
        assert name.is_required() is True
        assert name.annotation == str
        assert name.default is PydanticUndefined
        assert name.metadata[0].min_length == 1
        assert name.metadata[1].max_length == 50
        assert name.metadata[2].strict is True

        role = fields['role']
        assert role.is_required() is False
        assert role.annotation == Literal["USER", "ADMIN", "SYSTEM", "MANAGER"]
        assert role.default == "USER"

        last_login = fields['last_login']
        assert last_login.is_required() is False
        assert last_login.annotation == Optional[datetime]
        assert last_login.default is None

        created_by = fields['created_by']
        assert created_by.is_required() is False
        assert created_by.annotation == Optional[int]
        assert created_by.default is None

        updated_by = fields['updated_by']
        assert updated_by.is_required() is False
        assert updated_by.annotation == Optional[int]
        assert updated_by.default is None

        model_config = UserResponse.model_config
        assert model_config['from_attributes'] is True

    @pytest.mark.asyncio
    async def test_user_response_model_validate(self, db_session: AsyncSession):
        """Test that the user response schema model validate"""
        model = Users(
            username="testresponse",
            email="test@response.com",
            name="Test Response User",
            password="hashedpassword123",
            role="ADMIN",
            is_active=True
        )
        await save_object(db_session, model)

        query = select(Users).where(Users.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_schema_object = UserResponse.model_validate(db_model)

        assert db_schema_object == UserResponse(
            id=model.id,
            username="testresponse",
            email="test@response.com",
            name="Test Response User",
            role="ADMIN",
            is_active=True,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=None,
            created_by=model.created_by,
            updated_by=model.updated_by,
            sequence=model.sequence
        )

    @pytest.mark.asyncio
    async def test_user_response_model_validate_updated(self, db_session: AsyncSession):
        """Test that the user response schema model validate updated"""
        model = Users(
            username="testresponse",
            email="test@response.com",
            name="Test Response User",
            password="hashedpassword123",
            role="ADMIN",
            is_active=True
        )
        await save_object(db_session, model)

        query = select(Users).where(Users.id == model.id)
        result = await db_session.execute(query)
        db_model = result.scalar_one_or_none()

        db_model.username = "updatedresponse"
        db_model.email = "updated@response.com"
        db_model.name = "Updated Response User"
        db_model.role = "USER"
        db_model.is_active = False

        db_schema_object = UserResponse.model_validate(db_model)

        assert db_schema_object == UserResponse(
            id=model.id,
            username="updatedresponse",
            email="updated@response.com",
            name="Updated Response User",
            role="USER",
            is_active=False,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=None,
            created_by=model.created_by,
            updated_by=model.updated_by,
            sequence=model.sequence
        )


class TestUserLogin:
    """Test cases for the user login schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.login_dict = {
            "username": "testuser",
            "password": "password123"
        }

    def test_user_login_schema_inheritance(self):
        """Test that the user login schema inherits from BaseSchema"""
        assert issubclass(UserLogin, BaseSchema)

    def test_user_login_fields_inheritance(self):
        """Test that the user login schema has correct fields"""
        fields = UserLogin.model_fields
        assert len(fields) == 2
        assert 'username' in fields
        assert 'password' in fields

        username = fields['username']
        assert username.is_required() is True
        assert username.annotation == str
        assert username.default is PydanticUndefined
        assert username.metadata[0].strict is True

        password = fields['password']
        assert password.is_required() is True
        assert password.annotation == str
        assert password.default is PydanticUndefined
        assert password.metadata[0].strict is True

    def test_user_login_schema_input(self):
        schema = UserLogin(**self.login_dict)
        assert schema.username == "testuser"
        assert schema.password == "password123"

    def test_user_login_schema_input_updated(self):
        schema = UserLogin(**self.login_dict)
        assert schema.username == "testuser"
        assert schema.password == "password123"
        schema.username = "updateduser"
        schema.password = "updatedpassword123"
        assert schema.username == "updateduser"

    def test_user_login_schema_model_dump(self):
        schema = UserLogin(**self.login_dict)
        assert schema.model_dump() == {
            "username": "testuser",
            "password": "password123"
        }

    def test_user_login_schema_model_dump_json(self):
        schema = UserLogin(**self.login_dict)
        assert schema.model_dump_json() == '{'\
            '"username":"testuser",'\
            '"password":"password123"'\
            '}'


class TestUserChangePassword:
    """Test cases for the user change password schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.change_password_dict = {
            "current_password": "oldpassword123",
            "new_password": "newpassword456"
        }

    def test_user_change_password_schema_inheritance(self):
        """Test that the user change password schema inherits from BaseSchema"""
        assert issubclass(UserChangePassword, BaseSchema)

    def test_user_change_password_fields_inheritance(self):
        """Test that the user change password schema has correct fields"""
        fields = UserChangePassword.model_fields
        assert len(fields) == 2
        assert 'current_password' in fields
        assert 'new_password' in fields

        current_password = fields['current_password']
        assert current_password.is_required() is True
        assert current_password.annotation == str
        assert current_password.default is PydanticUndefined
        assert current_password.metadata[0].strict is True

        new_password = fields['new_password']
        assert new_password.is_required() is True
        assert new_password.annotation == str
        assert new_password.default is PydanticUndefined
        assert new_password.metadata[0].strict is True

    def test_user_change_password_schema_input(self):
        schema = UserChangePassword(**self.change_password_dict)
        assert schema.current_password == "oldpassword123"
        assert schema.new_password == "newpassword456"

    def test_user_change_password_schema_input_updated(self):
        schema = UserChangePassword(**self.change_password_dict)
        assert schema.current_password == "oldpassword123"
        assert schema.new_password == "newpassword456"
        schema.current_password = "updatedoldpassword123"
        schema.new_password = "updatednewpassword456"
        assert schema.current_password == "updatedoldpassword123"

    def test_user_change_password_schema_model_dump(self):
        schema = UserChangePassword(**self.change_password_dict)
        assert schema.model_dump() == {
            "current_password": "oldpassword123",
            "new_password": "newpassword456"
        }

    def test_user_change_password_schema_model_dump_json(self):
        schema = UserChangePassword(**self.change_password_dict)
        assert schema.model_dump_json() == '{'\
            '"current_password":"oldpassword123",'\
            '"new_password":"newpassword456"'\
            '}'


class TestToken:
    """Test cases for the token schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.token_dict = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }

    def test_token_schema_inheritance(self):
        """Test that the token schema inherits from BaseSchema"""
        assert issubclass(Token, BaseSchema)

    def test_token_fields_inheritance(self):
        """Test that the token schema has correct fields"""
        fields = Token.model_fields
        assert len(fields) == 3
        assert 'access_token' in fields
        assert 'refresh_token' in fields
        assert 'token_type' in fields

        access_token = fields['access_token']
        assert access_token.is_required() is True
        assert access_token.annotation == str
        assert access_token.default is PydanticUndefined

        refresh_token = fields['refresh_token']
        assert refresh_token.is_required() is True
        assert refresh_token.annotation == str
        assert refresh_token.default is PydanticUndefined

        token_type = fields['token_type']
        assert token_type.is_required() is False
        assert token_type.annotation == str
        assert token_type.default == "bearer"

    def test_token_schema_input(self):
        schema = Token(**self.token_dict)
        assert schema.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert schema.refresh_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert schema.token_type == "bearer"

    def test_token_schema_default_token_type(self):
        """Test that default token_type is bearer"""
        token_dict_no_type = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        schema = Token(**token_dict_no_type)
        assert schema.token_type == "bearer"

    def test_token_schema_model_dump(self):
        schema = Token(**self.token_dict)
        assert schema.model_dump() == {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }

    def test_token_schema_model_dump_json(self):
        schema = Token(**self.token_dict)
        assert schema.model_dump_json() == '{'\
            '"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",'\
            '"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",'\
            '"token_type":"bearer"'\
            '}'


class TestTokenRefresh:
    """Test cases for the token refresh schema"""

    @pytest.fixture(autouse=True)
    def setup_objects(self):
        """Setup method for the test suite"""
        self.token_refresh_dict = {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }

    def test_token_refresh_schema_inheritance(self):
        """Test that the token refresh schema inherits from BaseSchema"""
        assert issubclass(TokenRefresh, BaseSchema)

    def test_token_refresh_fields_inheritance(self):
        """Test that the token refresh schema has correct fields"""
        fields = TokenRefresh.model_fields
        assert len(fields) == 1
        assert 'refresh_token' in fields

        refresh_token = fields['refresh_token']
        assert refresh_token.is_required() is True
        assert refresh_token.annotation == str
        assert refresh_token.default is PydanticUndefined

    def test_token_refresh_schema_input(self):
        schema = TokenRefresh(**self.token_refresh_dict)
        assert schema.refresh_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    def test_token_refresh_schema_model_dump(self):
        schema = TokenRefresh(**self.token_refresh_dict)
        assert schema.model_dump() == {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }

    def test_token_refresh_schema_model_dump_json(self):
        schema = TokenRefresh(**self.token_refresh_dict)
        assert schema.model_dump_json() == '{'\
            '"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."'\
            '}'
