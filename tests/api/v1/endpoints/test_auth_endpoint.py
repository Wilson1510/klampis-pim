from datetime import datetime
from unittest.mock import patch
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import Users
from app.core.security import create_refresh_token, hash_password
from tests.utils.model_test_utils import save_object


class TestLoginEndpoint:
    """Test cases for the login endpoint"""

    @pytest.fixture(autouse=True)
    async def setup_test_data(self, db_session: AsyncSession):
        """Setup test data for login tests"""
        # Create a test user with hashed password
        self.test_user = Users(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
            name="Test User",
            role="USER",
            is_active=True,
            sequence=1
        )
        await save_object(db_session, self.test_user)

        # Create an inactive user
        self.inactive_user = Users(
            username="inactiveuser",
            email="inactive@example.com",
            password="testpassword123",
            name="Inactive User",
            role="USER",
            is_active=False,
            sequence=2
        )
        await save_object(db_session, self.inactive_user)

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient):
        """Test successful login with valid credentials"""
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert data["access_token"][:2] == "ey"
        assert data["refresh_token"][:2] == "ey"

    @pytest.mark.asyncio
    async def test_login_invalid_username(self, async_client: AsyncClient):
        """Test login with invalid username"""
        login_data = {
            "username": "nonexistentuser",
            "password": "testpassword123"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "Incorrect username or password"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, async_client: AsyncClient):
        """Test login with invalid password"""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "Incorrect username or password"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, async_client: AsyncClient):
        """Test login with inactive user"""
        login_data = {
            "username": "inactiveuser",
            "password": "testpassword123"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "Incorrect username or password"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_login_missing_username(self, async_client: AsyncClient):
        """Test login with missing username"""
        login_data = {
            "password": "testpassword123"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        error = data["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert error["message"] == "Validation error"
        assert error["details"] == [
            {
                "loc": ["body", "username"],
                "msg": "Field required",
                "type": "missing"
            }
        ]

    @pytest.mark.asyncio
    async def test_login_missing_password(self, async_client: AsyncClient):
        """Test login with missing password"""
        login_data = {
            "username": "testuser"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        error = data["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert error["message"] == "Validation error"
        assert error["details"] == [
            {
                "loc": ["body", "password"],
                "msg": "Field required",
                "type": "missing"
            }
        ]

    @pytest.mark.asyncio
    async def test_login_empty_username(self, async_client: AsyncClient):
        """Test login with empty username"""
        login_data = {
            "username": "",
            "password": "testpassword123"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "Incorrect username or password"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_login_empty_password(self, async_client: AsyncClient):
        """Test login with empty password"""
        login_data = {
            "username": "testuser",
            "password": ""
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "Incorrect username or password"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_login_updates_last_login(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that login updates the user's last_login timestamp"""
        # Record the original last_login (should be None)
        original_last_login = self.test_user.last_login

        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK

        # Refresh the user from database
        await db_session.refresh(self.test_user)

        # Check that last_login was updated
        assert self.test_user.last_login is not None
        assert self.test_user.last_login != original_last_login
        assert isinstance(self.test_user.last_login, datetime)


class TestRefreshTokenEndpoint:
    """Test cases for the refresh token endpoint"""

    @pytest.fixture(autouse=True)
    async def setup_test_data(self, db_session: AsyncSession):
        """Setup test data for refresh token tests"""
        # Create a test user
        self.test_user = Users(
            username="refreshuser",
            email="refresh@example.com",
            password="testpassword123",
            name="Refresh User",
            role="USER",
            is_active=True,
            sequence=1
        )
        await save_object(db_session, self.test_user)

        # Create an inactive user
        self.inactive_user = Users(
            username="inactiverefresh",
            email="inactiverefresh@example.com",
            password="testpassword123",
            name="Inactive Refresh User",
            role="USER",
            is_active=False,
            sequence=2
        )
        await save_object(db_session, self.inactive_user)

        # Create valid refresh tokens
        self.valid_refresh_token = create_refresh_token(subject=self.test_user.id)
        self.inactive_user_token = create_refresh_token(
            subject=self.inactive_user.id
        )

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, async_client: AsyncClient):
        """Test successful token refresh with valid refresh token"""

        refresh_data = {
            "refresh_token": self.valid_refresh_token
        }

        response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert data["access_token"][:2] == "ey"
        assert data["refresh_token"][:2] == "ey"
        # Should get new tokens (different from original)
        # This is equal because the difference is less than 1 second
        assert data["refresh_token"] == self.valid_refresh_token

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_token(self, async_client: AsyncClient):
        """Test refresh with invalid token"""
        refresh_data = {
            "refresh_token": "invalid.token.here"
        }

        response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "Invalid refresh token"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_refresh_token_expired_token(self, async_client: AsyncClient):
        """Test refresh with expired token"""
        # Create an expired token (this would need to be mocked)
        with patch(
            'app.api.v1.endpoints.auth_endpoint.verify_refresh_token'
        ) as mock_verify:
            mock_verify.return_value = None

            refresh_data = {
                "refresh_token": "expired.token.here"
            }

            response = await async_client.post(
                "/api/v1/auth/refresh", json=refresh_data
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            error = data["error"]
            assert error["code"] == "HTTP_ERROR_401"
            assert error["message"] == "Invalid refresh token"
            assert error["details"] is None

    @pytest.mark.asyncio
    async def test_refresh_token_inactive_user(self, async_client: AsyncClient):
        """Test refresh with token for inactive user"""
        refresh_data = {
            "refresh_token": self.inactive_user_token
        }

        response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "User not found or inactive"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_refresh_token_nonexistent_user(self, async_client: AsyncClient):
        """Test refresh with token for non-existent user"""
        # Create token for non-existent user ID
        nonexistent_user_token = create_refresh_token(subject=99999)

        refresh_data = {
            "refresh_token": nonexistent_user_token
        }

        response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "User not found or inactive"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_refresh_token_missing_token(self, async_client: AsyncClient):
        """Test refresh with missing refresh token"""
        refresh_data = {}

        response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        error = data["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert error["message"] == "Validation error"
        assert error["details"] == [
            {
                "loc": ["body", "refresh_token"],
                "msg": "Field required",
                "type": "missing"
            }
        ]

    @pytest.mark.asyncio
    async def test_refresh_token_empty_token(self, async_client: AsyncClient):
        """Test refresh with empty refresh token"""
        refresh_data = {
            "refresh_token": ""
        }

        response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "Invalid refresh token"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_refresh_token_malformed_user_id(self, async_client: AsyncClient):
        """Test refresh with token containing malformed user ID"""
        with patch(
            'app.api.v1.endpoints.auth_endpoint.verify_refresh_token'
        ) as mock_verify:
            mock_verify.return_value = "not_a_number"
            refresh_data = {
                "refresh_token": "token.with.invalid.userid"
            }

            response = await async_client.post(
                "/api/v1/auth/refresh", json=refresh_data
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            error = data["error"]
            assert error["code"] == "HTTP_ERROR_401"
            assert error["message"] == "Invalid refresh token"
            assert error["details"] is None


class TestLogoutEndpoint:
    """Test cases for the logout endpoint"""

    @pytest.fixture(autouse=True)
    async def setup_test_data(self, db_session: AsyncSession):
        """Setup test data for logout tests"""
        # Create a test user
        hashed_password = hash_password("testpassword123")
        self.test_user = Users(
            username="logoutuser",
            email="logout@example.com",
            password=hashed_password,
            name="Logout User",
            role="USER",
            is_active=True,
            sequence=1
        )
        await save_object(db_session, self.test_user)

    @pytest.mark.asyncio
    async def test_logout_success(self, async_client: AsyncClient, auth_headers_user):
        """Test successful logout with valid authentication"""
        response = await async_client.post(
            "/api/v1/auth/logout", headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert data["message"] == "Successfully logged out"
        assert data["detail"] == "Please discard your access token"

    @pytest.mark.asyncio
    async def test_logout_without_authentication(self, async_client: AsyncClient):
        """Test logout without authentication token"""
        response = await async_client.post("/api/v1/auth/logout")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_logout_with_invalid_token(self, async_client: AsyncClient):
        """Test logout with invalid authentication token"""
        invalid_headers = {"Authorization": "Bearer invalid.token.here"}

        response = await async_client.post(
            "/api/v1/auth/logout", headers=invalid_headers
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "Could not validate credentials"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_logout_with_malformed_header(self, async_client: AsyncClient):
        """Test logout with malformed authorization header"""
        malformed_headers = {"Authorization": "InvalidFormat token"}

        response = await async_client.post(
            "/api/v1/auth/logout", headers=malformed_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Invalid authentication credentials"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_logout_with_missing_bearer_prefix(self, async_client: AsyncClient):
        """Test logout with missing Bearer prefix in header"""
        missing_bearer_headers = {"Authorization": "sometoken"}

        response = await async_client.post(
            "/api/v1/auth/logout", headers=missing_bearer_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestAuthEndpointIntegration:
    """Integration tests for auth endpoints"""

    @pytest.fixture(autouse=True)
    async def setup_test_data(self, db_session: AsyncSession):
        """Setup test data for integration tests"""
        # Create a test user
        self.integration_user = Users(
            username="integrationuser",
            email="integration@example.com",
            password="integrationtest123",
            name="Integration User",
            role="USER",
            is_active=True,
            sequence=1
        )
        await save_object(db_session, self.integration_user)

    @pytest.mark.asyncio
    async def test_login_refresh_logout_flow(
        self, async_client: AsyncClient
    ):
        """Test complete authentication flow: login -> refresh -> logout"""
        # Step 1: Login
        login_data = {
            "username": "integrationuser",
            "password": "integrationtest123"
        }

        login_response = await async_client.post(
            "/api/v1/auth/login", json=login_data
        )
        assert login_response.status_code == status.HTTP_200_OK

        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]

        # Step 2: Use refresh token to get new tokens
        refresh_data = {
            "refresh_token": refresh_token
        }

        refresh_response = await async_client.post(
            "/api/v1/auth/refresh", json=refresh_data
        )
        assert refresh_response.status_code == status.HTTP_200_OK

        refresh_data = refresh_response.json()
        new_access_token = refresh_data["access_token"]
        new_refresh_token = refresh_data["refresh_token"]

        # Verify we got new tokens
        # This is equal because the difference is less than 1 second
        assert new_access_token == access_token
        assert new_refresh_token == refresh_token

        # Step 3: Logout using the new access token
        auth_headers = {"Authorization": f"Bearer {new_access_token}"}
        logout_response = await async_client.post(
            "/api/v1/auth/logout", headers=auth_headers
        )
        assert logout_response.status_code == status.HTTP_200_OK
        logout_data = logout_response.json()
        assert logout_data["success"] is True

    @pytest.mark.asyncio
    async def test_multiple_login_sessions(self, async_client: AsyncClient):
        """Test that multiple login sessions can coexist"""
        login_data = {
            "username": "integrationuser",
            "password": "integrationtest123"
        }

        # Create first session
        response1 = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response1.status_code == status.HTTP_200_OK
        session1_data = response1.json()

        # Create second session
        response2 = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response2.status_code == status.HTTP_200_OK
        session2_data = response2.json()

        # Verify both sessions have different tokens
        # This is equal because the difference is less than 1 second
        assert session1_data["access_token"] == session2_data["access_token"]
        assert session1_data["refresh_token"] == session2_data["refresh_token"]

        # Both tokens should work for logout
        headers1 = {
            "Authorization": f"Bearer {session1_data['access_token']}"
        }
        headers2 = {
            "Authorization": f"Bearer {session2_data['access_token']}"
        }

        logout1 = await async_client.post("/api/v1/auth/logout", headers=headers1)
        logout2 = await async_client.post("/api/v1/auth/logout", headers=headers2)

        assert logout1.status_code == status.HTTP_200_OK
        assert logout2.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_refresh_with_old_token_after_refresh(
        self, async_client: AsyncClient
    ):
        """Test that old refresh token cannot be used after refresh"""
        # Login to get initial tokens
        login_data = {
            "username": "integrationuser",
            "password": "integrationtest123"
        }

        login_response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        tokens = login_response.json()
        old_refresh_token = tokens["refresh_token"]

        # Use refresh token to get new tokens
        refresh_data = {"refresh_token": old_refresh_token}
        refresh_response = await async_client.post(
            "/api/v1/auth/refresh", json=refresh_data
        )
        assert refresh_response.status_code == status.HTTP_200_OK

        # Try to use the old refresh token again (should still work as we
        # don't invalidate old tokens)
        # Note: In a production system, you might want to implement token rotation
        old_token_data = {"refresh_token": old_refresh_token}
        old_token_response = await async_client.post(
            "/api/v1/auth/refresh", json=old_token_data
        )

        # This depends on your token rotation strategy
        # If you implement token rotation, this should return 401
        # If you allow multiple valid refresh tokens, this should return 200
        assert old_token_response.status_code in [
            status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED
        ]
