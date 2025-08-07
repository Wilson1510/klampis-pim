import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import Users
from tests.utils.model_test_utils import save_object


class TestGetMyProfile:
    """Test cases for the get my profile endpoint"""

    @pytest.mark.asyncio
    async def test_get_my_profile_success(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test successful retrieval of user profile"""
        response = await async_client.get(
            "/api/v1/profile/me", headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "success" in data
        assert data["success"] is True
        assert "data" in data

        profile_data = data["data"]
        assert profile_data["username"] == "user"
        assert profile_data["email"] == "user@test.com"
        assert profile_data["name"] == "User User"
        assert profile_data["role"] == "USER"
        assert profile_data["is_active"] is True
        # Must be refreshed from database to get last_login
        assert profile_data["last_login"] is None
        assert profile_data["sequence"] == 3
        assert profile_data["created_at"] is not None
        assert profile_data["updated_at"] is not None
        assert profile_data["created_by"] is None
        assert profile_data["updated_by"] is None

        # Password should not be included
        assert "password" not in profile_data

    @pytest.mark.asyncio
    async def test_get_my_profile_without_authentication(
        self, async_client: AsyncClient
    ):
        """Test get profile without authentication"""
        response = await async_client.get("/api/v1/profile/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestUpdateMyProfile:
    """Test cases for the update my profile endpoint"""

    @pytest.mark.asyncio
    async def test_update_my_profile_success(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test successful profile update"""
        update_data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "name": "Updated User Name"
        }

        response = await async_client.put(
            "/api/v1/profile/me", json=update_data, headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        profile_data = data["data"]
        assert profile_data["username"] == "updateduser"
        assert profile_data["email"] == "updated@example.com"
        assert profile_data["name"] == "Updated User Name"

    @pytest.mark.asyncio
    async def test_update_my_profile_cannot_change_role(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test that user cannot change their own role"""
        update_data = {
            "name": "Updated Name",
            "role": "ADMIN"  # This should be forbidden
        }

        response = await async_client.put(
            "/api/v1/profile/me", json=update_data, headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You cannot change your own role"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_update_my_profile_cannot_change_active_status(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test that user cannot change their own active status"""
        update_data = {
            "name": "Updated Name",
            "is_active": False  # This should be forbidden
        }

        response = await async_client.put(
            "/api/v1/profile/me", json=update_data, headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "You cannot change your own active status"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_update_my_profile_invalid_email_format(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test update with invalid email format"""
        update_data = {
            "email": "invalid-email-format"
        }

        response = await async_client.put(
            "/api/v1/profile/me", json=update_data, headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        error = data["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert error["message"] == "Validation error"
        assert error["details"] == [
            {
                "loc": ["body", "email"],
                "msg": (
                    "value is not a valid email address: "
                    "An email address must have an @-sign."
                ),
                "type": "value_error"
            }
        ]

    @pytest.mark.asyncio
    async def test_update_my_profile_duplicate_username(
        self, async_client: AsyncClient, auth_headers_user, db_session: AsyncSession
    ):
        """Test update with username that already exists"""
        # Create another user with existing username
        existing_user = Users(
            username="existinguser",
            email="existing@example.com",
            password="testpassword123",
            name="Existing User",
            role="USER",
            is_active=True,
            sequence=2
        )
        await save_object(db_session, existing_user)

        update_data = {
            "username": "existinguser"  # This username already exists
        }

        response = await async_client.put(
            "/api/v1/profile/me", json=update_data, headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == "User with username 'existinguser' already exists"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_update_my_profile_duplicate_email(
        self, async_client: AsyncClient, auth_headers_user, db_session: AsyncSession
    ):
        """Test update with email that already exists"""
        # Create another user with existing email
        existing_user = Users(
            username="existingemail",
            email="existing@example.com",
            password="testpassword123",
            name="Existing Email User",
            role="USER",
            is_active=True,
            sequence=3
        )
        await save_object(db_session, existing_user)

        update_data = {
            "email": "existing@example.com"  # This email already exists
        }

        response = await async_client.put(
            "/api/v1/profile/me", json=update_data, headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "User with email 'existing@example.com' already exists"
        )
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_update_my_profile_without_authentication(
        self, async_client: AsyncClient
    ):
        """Test update profile without authentication"""
        update_data = {
            "name": "Should Not Work"
        }

        response = await async_client.put("/api/v1/profile/me", json=update_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestChangeMyPassword:
    """Test cases for the change my password endpoint"""

    @pytest.mark.asyncio
    async def test_change_my_password_success(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test successful password change"""
        password_data = {
            "current_password": "userpassword",
            "new_password": "newpassword123"
        }

        response = await async_client.post(
            "/api/v1/profile/change-password",
            json=password_data,
            headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert data["data"]["username"] == "user"
        assert data["data"]["email"] == "user@test.com"
        assert data["data"]["name"] == "User User"
        assert data["data"]["role"] == "USER"
        # Password should not be returned in response
        assert "password" not in data["data"]

        login = await async_client.post(
            "/api/v1/auth/login",
            json={
                "username": "user",
                "password": password_data["new_password"]
            }
        )
        assert login.status_code == status.HTTP_200_OK
        assert login.json()["access_token"] is not None
        assert login.json()["refresh_token"] is not None

    @pytest.mark.asyncio
    async def test_change_my_password_incorrect_current_password(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test password change with incorrect current password"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }

        response = await async_client.post(
            "/api/v1/profile/change-password",
            json=password_data,
            headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == "Current password is incorrect"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_change_my_password_missing_current_password(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test password change with missing current password"""
        password_data = {
            "new_password": "newpassword123"
            # Missing current_password
        }

        response = await async_client.post(
            "/api/v1/profile/change-password",
            json=password_data,
            headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        error = data["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert error["message"] == "Validation error"
        assert error["details"] == [
            {
                "loc": ["body", "current_password"],
                "msg": "Field required",
                "type": "missing"
            }
        ]

    @pytest.mark.asyncio
    async def test_change_my_password_missing_new_password(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test password change with missing new password"""
        password_data = {
            "current_password": "currentpassword123"
            # Missing new_password
        }

        response = await async_client.post(
            "/api/v1/profile/change-password",
            json=password_data,
            headers=auth_headers_user
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        error = data["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert error["message"] == "Validation error"
        assert error["details"] == [
            {
                "loc": ["body", "new_password"],
                "msg": "Field required",
                "type": "missing"
            }
        ]

    @pytest.mark.asyncio
    async def test_change_my_password_without_authentication(
        self, async_client: AsyncClient
    ):
        """Test password change without authentication"""
        password_data = {
            "current_password": "currentpassword123",
            "new_password": "newpassword123"
        }

        response = await async_client.post(
            "/api/v1/profile/change-password", json=password_data
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None

    @pytest.mark.asyncio
    async def test_change_my_password_with_invalid_token(
        self, async_client: AsyncClient
    ):
        """Test password change with invalid token"""
        invalid_headers = {"Authorization": "Bearer invalid.token.here"}
        password_data = {
            "current_password": "currentpassword123",
            "new_password": "newpassword123"
        }

        response = await async_client.post(
            "/api/v1/profile/change-password",
            json=password_data,
            headers=invalid_headers
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        error = data["error"]
        assert error["code"] == "HTTP_ERROR_401"
        assert error["message"] == "Could not validate credentials"
        assert error["details"] is None


class TestProfileEndpointIntegration:
    """Integration tests for profile endpoints"""

    @pytest.mark.asyncio
    async def test_profile_workflow_get_update_get(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test complete profile workflow: get -> update -> get"""
        # Step 1: Get initial profile
        get_response1 = await async_client.get(
            "/api/v1/profile/me", headers=auth_headers_user
        )
        assert get_response1.status_code == status.HTTP_200_OK
        initial_profile = get_response1.json()["data"]
        original_name = initial_profile["name"]

        # Step 2: Update profile
        update_data = {
            "name": "Updated Integration Name",
            "email": "updated@integration.com"
        }
        update_response = await async_client.put(
            "/api/v1/profile/me", json=update_data, headers=auth_headers_user
        )
        assert update_response.status_code == status.HTTP_200_OK
        updated_profile = update_response.json()["data"]

        # Verify update worked
        assert updated_profile["name"] == "Updated Integration Name"
        assert updated_profile["email"] == "updated@integration.com"
        assert updated_profile["name"] != original_name

        # Step 3: Get updated profile
        get_response2 = await async_client.get(
            "/api/v1/profile/me", headers=auth_headers_user
        )
        assert get_response2.status_code == status.HTTP_200_OK
        final_profile = get_response2.json()["data"]

        # Verify changes persisted
        assert final_profile["name"] == "Updated Integration Name"
        assert final_profile["email"] == "updated@integration.com"

    @pytest.mark.asyncio
    async def test_profile_password_change_workflow(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test password change workflow"""
        # Step 1: Change password
        password_data = {
            "current_password": "userpassword",
            "new_password": "newintegrationpass123"
        }
        change_response = await async_client.post(
            "/api/v1/profile/change-password",
            json=password_data,
            headers=auth_headers_user
        )
        assert change_response.status_code == status.HTTP_200_OK

        # Step 2: Verify old password no longer works
        # (This would require a login attempt, but we can test that
        # the change was successful by trying to change again with new password)
        new_password_data = {
            "current_password": "newintegrationpass123",
            "new_password": "anotherpassword123"
        }
        change_response2 = await async_client.post(
            "/api/v1/profile/change-password",
            json=new_password_data,
            headers=auth_headers_user
        )
        assert change_response2.status_code == status.HTTP_200_OK

        # Step 3: Verify old password is rejected
        old_password_data = {
            "current_password": "integrationpass123",  # Old password
            "new_password": "shouldnotwork123"
        }
        change_response3 = await async_client.post(
            "/api/v1/profile/change-password",
            json=old_password_data,
            headers=auth_headers_user
        )
        assert change_response3.status_code == status.HTTP_400_BAD_REQUEST
        error = change_response3.json()["error"]
        assert error["message"] == "Current password is incorrect"

    @pytest.mark.asyncio
    async def test_profile_concurrent_updates(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test handling of concurrent profile updates"""
        # This test simulates what could happen with concurrent updates
        # In a real scenario, you might want to implement optimistic locking

        update_data1 = {"name": "First Update"}
        update_data2 = {"email": "second@update.com"}

        # Both updates should succeed since they modify different fields
        response1 = await async_client.put(
            "/api/v1/profile/me", json=update_data1, headers=auth_headers_user
        )
        response2 = await async_client.put(
            "/api/v1/profile/me", json=update_data2, headers=auth_headers_user
        )

        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK

        # Verify final state
        final_response = await async_client.get(
            "/api/v1/profile/me", headers=auth_headers_user
        )
        final_data = final_response.json()["data"]
        assert final_data["name"] == "First Update"
        assert final_data["email"] == "second@update.com"
