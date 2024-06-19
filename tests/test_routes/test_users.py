import pytest
from fastapi import status

from posts_app import schemas

base_endpoint = "/api/users"


pytestmark = pytest.mark.usefixtures("api_client", "session")


class TestUserAccountRetrievals:
    def test_retrieve_users_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot retrieve users."""
        response = api_client.get(base_endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}


class TestUserAccountCreation:
    def test_create_user(self, api_client):
        """Test the creation of a single user."""
        response = api_client.post(
            base_endpoint,
            json={"email": "testuser@email.com", "password": "password1234"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        new_user = schemas.User(**response.json())
        assert new_user.email == "testuser@email.com"
        assert new_user.id is not None

    @pytest.mark.parametrize(
        "email, password, expected_status",
        [
            ("", "password1234", status.HTTP_422_UNPROCESSABLE_ENTITY),
            (
                "testuser",
                "password1234",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                "testuseremail.com",
                "password1234",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            ("user@email.com", "", status.HTTP_422_UNPROCESSABLE_ENTITY),
            ("user@email.com", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ],
    )
    def test_create_user_invalid_data(
        self, api_client, email, password, expected_status
    ):
        """Test user creation with invalid data."""
        response = api_client.post(
            base_endpoint, json={"email": email, "password": password}
        )
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "email, password, expected",
        [
            # Happy path tests
            ("test@example.com", "password123", status.HTTP_201_CREATED),
            ("user@domain.com", "securepassword", status.HTTP_201_CREATED),
            (
                "another.user@domain.com",
                "anotherpassword",
                status.HTTP_201_CREATED,
            ),
            # Edge cases
            (
                "",
                "password123",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # Empty email
            (
                "test@example.com",
                "",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # Empty password
            (
                "a@b.c",
                "short",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # Password too short
            (
                "longemailaddress@domain.com",
                "longpassword" * 10,
                status.HTTP_201_CREATED,
            ),  # Long email and password
            # Error cases
            (
                "invalid-email",
                "password123",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # Invalid email format
            (
                "test@example.com",
                "short",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # Password too short
            (
                "user@domain.com",
                None,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # None password
            (
                None,
                "password123",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),  # None email
        ],
        ids=[
            "valid_email_password_1",
            "valid_email_password_2",
            "valid_email_password_3",
            "empty_email",
            "empty_password",
            "minimal_valid_email_short_password",
            "long_email_long_password",
            "invalid_email_format",
            "short_password",
            "none_password",
            "none_email",
        ],
    )
    def test_create_multiple_users(
        self, api_client, email, password, expected
    ):
        """Test creating multiple users with different data."""
        response = api_client.post(
            base_endpoint, json={"email": email, "password": password}
        )

        assert response.status_code == expected
