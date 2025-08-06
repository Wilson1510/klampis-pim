from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import Users
from tests.utils.model_test_utils import save_object


class TestGetUsers:
    """Test cases for GET /users/ endpoint."""

    async def test_get_users_success(
        self, async_client: AsyncClient, auth_headers_admin
    ):
        """Test getting users successfully."""
        response = await async_client.get(
            "/api/v1/users/", headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()["data"]

        # Should have at least system, admin, and user from fixtures
        assert len(data) == 2

        # Verify response structure
        names = {item["name"] for item in data}
        expected_names = {
            "System User",
            "Admin User"
        }
        assert names == expected_names

        for item in data:
            assert "username" in item
            assert "email" in item
            assert "name" in item
            assert "role" in item
            assert "is_active" in item
            assert "last_login" in item

    async def test_get_users_filter_by_username(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test filtering by username."""
        # Create test user
        test_user = Users(
            username="testfilter",
            email="testfilter@example.com",
            password="testpassword123",
            name="Test Filter User",
            role="USER",
            is_active=True,
            sequence=10
        )
        await save_object(db_session, test_user)

        response = await async_client.get(
            "/api/v1/users/?username=testfilter", headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["username"] == "testfilter"

    async def test_get_users_filter_by_email(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test filtering by email."""
        # Create test user
        test_user = Users(
            username="emailfilteruser",
            email="emailfilter@example.com",
            password="testpassword123",
            name="Email Filter User",
            role="USER",
            is_active=True,
            sequence=11
        )
        await save_object(db_session, test_user)

        response = await async_client.get(
            "/api/v1/users/?email=emailfilter", headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["email"] == "emailfilter@example.com"

    async def test_get_users_filter_by_name(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test filtering by name."""
        # Create test user
        test_user = Users(
            username="namefilteruser",
            email="namefilter@example.com",
            password="testpassword123",
            name="Name Filter User",
            role="USER",
            is_active=True,
            sequence=12
        )
        await save_object(db_session, test_user)

        response = await async_client.get(
            "/api/v1/users/?name=Name Filter", headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["name"] == "Name Filter User"

    async def test_get_users_filter_by_role(
        self, async_client: AsyncClient, auth_headers_admin
    ):
        """Test filtering by role."""
        response = await async_client.get(
            "/api/v1/users/?role=ADMIN", headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["role"] == "ADMIN"

    async def test_get_users_filter_by_is_active(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test filtering by is_active status."""
        # Create inactive user
        inactive_user = Users(
            username="inactiveuser",
            email="inactive@example.com",
            password="testpassword123",
            name="Inactive User",
            role="USER",
            is_active=False,
            sequence=13
        )
        await save_object(db_session, inactive_user)

        # Test active filter
        response = await async_client.get(
            "/api/v1/users/?is_active=true", headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        for user in data:
            assert user["is_active"] is True

        # Test inactive filter
        response = await async_client.get(
            "/api/v1/users/?is_active=false", headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        for user in data:
            assert user["is_active"] is False

    async def test_get_users_combined_filters(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test combining multiple filters."""
        # Create test user
        test_user = Users(
            username="combined",
            email="combined@example.com",
            password="testpassword123",
            name="Combined Filter User",
            role="USER",
            is_active=True,
            sequence=14
        )
        await save_object(db_session, test_user)

        response = await async_client.get(
            "/api/v1/users/?username=combined&role=USER&is_active=true",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["username"] == "combined"
        assert data[0]["role"] == "USER"
        assert data[0]["is_active"] is True

    async def test_get_users_by_user(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test getting users by manager."""
        response = await async_client.get(
            "/api/v1/users/", headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Admin access required"
        assert error["details"] is None

    async def test_get_users_unauthenticated(
        self, async_client: AsyncClient
    ):
        """Test getting users without authentication."""
        response = await async_client.get("/api/v1/users/")
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestCreateUser:
    """Test cases for POST /users/ endpoint."""

    async def test_create_user_success(
        self, async_client: AsyncClient, auth_headers_admin
    ):
        """Test creating user successfully."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "name": "New User",
            "role": "USER"
        }

        response = await async_client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_admin
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert data["role"] == "USER"
        assert data["is_active"] is True
        # Password should not be returned
        assert "password" not in data

    async def test_create_user_duplicate_username(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test creating user with duplicate username."""
        # Create existing user
        existing_user = Users(
            username="duplicateuser",
            email="duplicate@example.com",
            password="testpassword123",
            name="Duplicate User",
            role="USER",
            is_active=True,
            sequence=15
        )
        await save_object(db_session, existing_user)

        user_data = {
            "username": "duplicateuser",
            "email": "different@example.com",
            "password": "newpassword123",
            "name": "Different User",
            "role": "USER"
        }
        response = await async_client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_admin
        )
        error = response.json()["error"]

        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == "User with username 'duplicateuser' already exists"
        assert error["details"] is None

    async def test_create_user_duplicate_email(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test creating user with duplicate email."""
        # Create existing user
        existing_user = Users(
            username="existinguser",
            email="duplicate@example.com",
            password="testpassword123",
            name="Existing User",
            role="USER",
            is_active=True,
            sequence=16
        )
        await save_object(db_session, existing_user)

        user_data = {
            "username": "differentuser",
            "email": "duplicate@example.com",
            "password": "newpassword123",
            "name": "Different User",
            "role": "USER"
        }
        response = await async_client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_admin
        )
        error = response.json()["error"]

        assert response.status_code == 400
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "User with email 'duplicate@example.com' already exists"
        )
        assert error["details"] is None

    async def test_create_user_by_user(
        self, async_client: AsyncClient, auth_headers_user
    ):
        """Test creating user by regular user (should be forbidden)."""
        user_data = {
            "username": "forbiddenuser",
            "email": "forbidden@example.com",
            "password": "forbiddenpassword123",
            "name": "Forbidden User",
            "role": "USER"
        }

        response = await async_client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Admin access required"
        assert error["details"] is None

    async def test_create_user_unauthenticated(
        self, async_client: AsyncClient
    ):
        """Test creating user without authentication."""
        user_data = {
            "username": "unauthuser",
            "email": "unauth@example.com",
            "password": "unauthpassword123",
            "name": "Unauth User",
            "role": "USER"
        }

        response = await async_client.post(
            "/api/v1/users/", json=user_data
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestGetUser:
    """Test cases for GET /users/{id} endpoint."""

    async def test_get_user_success(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test getting user by ID successfully."""
        # Create test user
        test_user = Users(
            username="gettestuser",
            email="gettest@example.com",
            password="testpassword123",
            name="Get Test User",
            role="USER",
            is_active=True,
            sequence=17
        )
        await save_object(db_session, test_user)

        response = await async_client.get(
            f"/api/v1/users/{test_user.id}", headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == test_user.id
        assert data["username"] == "gettestuser"
        assert data["email"] == "gettest@example.com"
        assert data["name"] == "Get Test User"
        # Password should not be returned
        assert "password" not in data

    async def test_get_user_not_found(
        self, async_client: AsyncClient, auth_headers_admin
    ):
        """Test getting non-existent user."""
        response = await async_client.get(
            "/api/v1/users/999", headers=auth_headers_admin
        )
        error = response.json()["error"]

        assert response.status_code == 404
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "User with id 999 not found"
        assert error["details"] is None

    async def test_get_user_by_user(
        self, async_client: AsyncClient, auth_headers_user, db_session: AsyncSession
    ):
        """Test getting user by regular user (should be forbidden)."""
        # Create test user
        test_user = Users(
            username="usertestuser",
            email="usertest@example.com",
            password="testpassword123",
            name="User Test User",
            role="USER",
            is_active=True,
            sequence=19
        )
        await save_object(db_session, test_user)

        response = await async_client.get(
            f"/api/v1/users/{test_user.id}", headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Admin access required"
        assert error["details"] is None

    async def test_get_user_unauthenticated(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test getting user by ID without authentication."""
        # Create test user
        test_user = Users(
            username="unauthgettestuser",
            email="unauthgettest@example.com",
            password="testpassword123",
            name="Unauth Get Test User",
            role="USER",
            is_active=True,
            sequence=20
        )
        await save_object(db_session, test_user)

        response = await async_client.get(f"/api/v1/users/{test_user.id}")

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestUpdateUser:
    """Test cases for PUT /users/{id} endpoint."""

    async def test_update_user_success(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test updating user successfully."""
        # Create test user
        test_user = Users(
            username="updatetestuser",
            email="updatetest@example.com",
            password="testpassword123",
            name="Update Test User",
            role="USER",
            is_active=True,
            sequence=21
        )
        await save_object(db_session, test_user)

        update_data = {
            "name": "Updated Test User",
            "email": "updated@example.com"
        }
        response = await async_client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == test_user.id
        assert data["name"] == "Updated Test User"
        assert data["email"] == "updated@example.com"
        assert data["username"] == "updatetestuser"  # Unchanged

    async def test_update_user_not_found(
        self, async_client: AsyncClient, auth_headers_admin
    ):
        """Test updating non-existent user."""
        update_data = {"name": "Updated Name"}
        response = await async_client.put(
            "/api/v1/users/999999",
            json=update_data,
            headers=auth_headers_admin
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "User with id 999999 not found"
        assert error["details"] is None

    async def test_update_user_duplicate_username(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test updating user with duplicate username."""
        # Create existing users
        user1 = Users(
            username="existinguser1",
            email="existing1@example.com",
            password="testpassword123",
            name="Existing User 1",
            role="USER",
            is_active=True,
            sequence=22
        )
        user2 = Users(
            username="existinguser2",
            email="existing2@example.com",
            password="testpassword123",
            name="Existing User 2",
            role="USER",
            is_active=True,
            sequence=23
        )
        await save_object(db_session, user1)
        await save_object(db_session, user2)

        update_data = {"username": "existinguser1"}
        response = await async_client.put(
            f"/api/v1/users/{user2.id}",
            json=update_data,
            headers=auth_headers_admin
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "User with username 'existinguser1' already exists"
        )
        assert error["details"] is None

    async def test_update_user_duplicate_email(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test updating user with duplicate email."""
        # Create existing users
        user1 = Users(
            username="emailuser1",
            email="existing@example.com",
            password="testpassword123",
            name="Email User 1",
            role="USER",
            is_active=True,
            sequence=24
        )
        user2 = Users(
            username="emailuser2",
            email="different@example.com",
            password="testpassword123",
            name="Email User 2",
            role="USER",
            is_active=True,
            sequence=25
        )
        await save_object(db_session, user1)
        await save_object(db_session, user2)

        update_data = {"email": "existing@example.com"}
        response = await async_client.put(
            f"/api/v1/users/{user2.id}",
            json=update_data,
            headers=auth_headers_admin
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == (
            "User with email 'existing@example.com' already exists"
        )
        assert error["details"] is None

    async def test_update_user_by_user(
        self, async_client: AsyncClient, auth_headers_user, db_session: AsyncSession
    ):
        """Test updating user by regular user (should be forbidden)."""
        # Create test user
        test_user = Users(
            username="userupdateuser",
            email="userupdate@example.com",
            password="testpassword123",
            name="User Update User",
            role="USER",
            is_active=True,
            sequence=27
        )
        await save_object(db_session, test_user)

        update_data = {"name": "User Updated User"}
        response = await async_client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Admin access required"
        assert error["details"] is None

    async def test_update_user_unauthenticated(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test updating user without authentication."""
        # Create test user
        test_user = Users(
            username="unauthupdateuser",
            email="unauthupdate@example.com",
            password="testpassword123",
            name="Unauth Update User",
            role="USER",
            is_active=True,
            sequence=28
        )
        await save_object(db_session, test_user)

        update_data = {"name": "Unauth Updated User"}
        response = await async_client.put(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestDeleteUser:
    """Test cases for DELETE /users/{id} endpoint."""

    async def test_delete_user_success(
        self, async_client: AsyncClient, auth_headers_admin, db_session: AsyncSession
    ):
        """Test deleting user successfully."""
        # Create test user
        test_user = Users(
            username="deletetestuser",
            email="deletetest@example.com",
            password="testpassword123",
            name="Delete Test User",
            role="USER",
            is_active=True,
            sequence=29
        )
        await save_object(db_session, test_user)

        response = await async_client.delete(
            f"/api/v1/users/{test_user.id}", headers=auth_headers_admin
        )

        assert response.status_code == 204

    async def test_delete_user_not_found(
        self, async_client: AsyncClient, auth_headers_admin
    ):
        """Test deleting non-existent user."""
        response = await async_client.delete(
            "/api/v1/users/999999", headers=auth_headers_admin
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_404"
        assert error["message"] == "User with id 999999 not found"
        assert error["details"] is None

    async def test_delete_system_user(
        self, async_client: AsyncClient, auth_headers_admin
    ):
        """Test deleting system user (should be forbidden)."""
        # Try to delete system user (ID 1)
        response = await async_client.delete(
            "/api/v1/users/1", headers=auth_headers_admin
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == "Cannot delete system or admin user"
        assert error["details"] is None

    async def test_delete_admin_user(
        self, async_client: AsyncClient, auth_headers_admin
    ):
        """Test deleting admin user (should be forbidden)."""
        # Try to delete admin user (ID 2)
        response = await async_client.delete(
            "/api/v1/users/2", headers=auth_headers_admin
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_400"
        assert error["message"] == "Cannot delete system or admin user"
        assert error["details"] is None

    async def test_delete_user_by_user(
        self, async_client: AsyncClient, auth_headers_user, db_session: AsyncSession
    ):
        """Test deleting user by regular user (should be forbidden)."""
        # Create test user
        test_user = Users(
            username="userdeleteuser",
            email="userdelete@example.com",
            password="testpassword123",
            name="User Delete User",
            role="USER",
            is_active=True,
            sequence=31
        )
        await save_object(db_session, test_user)

        response = await async_client.delete(
            f"/api/v1/users/{test_user.id}", headers=auth_headers_user
        )

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Admin access required"
        assert error["details"] is None

    async def test_delete_user_unauthenticated(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test deleting user without authentication."""
        # Create test user
        test_user = Users(
            username="unauthdeleteuser",
            email="unauthdelete@example.com",
            password="testpassword123",
            name="Unauth Delete User",
            role="USER",
            is_active=True,
            sequence=32
        )
        await save_object(db_session, test_user)

        response = await async_client.delete(f"/api/v1/users/{test_user.id}")

        assert response.status_code == 403
        error = response.json()["error"]
        assert error["code"] == "HTTP_ERROR_403"
        assert error["message"] == "Not authenticated"
        assert error["details"] is None


class TestUserEndpointIntegration:
    """Integration tests for user endpoints."""

    async def test_full_crud_workflow(
        self, async_client: AsyncClient, auth_headers_admin
    ):
        """Test complete CRUD workflow for users."""
        # Create
        create_data = {
            "username": "cruduser",
            "email": "crud@example.com",
            "password": "crudpassword123",
            "name": "CRUD User",
            "role": "USER"
        }
        response = await async_client.post(
            "/api/v1/users/", json=create_data, headers=auth_headers_admin
        )
        assert response.status_code == 201
        created_data = response.json()["data"]
        user_id = created_data["id"]

        # Read individual
        response = await async_client.get(
            f"/api/v1/users/{user_id}", headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["username"] == "cruduser"
        assert data["email"] == "crud@example.com"
        assert data["name"] == "CRUD User"
        assert data["role"] == "USER"

        # Read list (should include our new user)
        response = await async_client.get(
            "/api/v1/users/?username=cruduser", headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["username"] == "cruduser"

        # Update
        update_data = {
            "name": "Updated CRUD User",
            "email": "updated-crud@example.com",
            "is_active": False
        }
        response = await async_client.put(
            f"/api/v1/users/{user_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Updated CRUD User"
        assert data["email"] == "updated-crud@example.com"
        assert data["is_active"] is False

        # Delete
        response = await async_client.delete(
            f"/api/v1/users/{user_id}", headers=auth_headers_admin
        )
        assert response.status_code == 204

        # Verify user is deleted
        response = await async_client.get(
            f"/api/v1/users/{user_id}", headers=auth_headers_admin
        )
        assert response.status_code == 404
        error = response.json()["error"]
        assert error["message"] == f"User with id {user_id} not found"
