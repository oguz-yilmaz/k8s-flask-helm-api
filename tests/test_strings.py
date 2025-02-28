import json
import random
import string
from http import HTTPStatus
from unittest.mock import patch

import pytest

from src.core.models.string import String
from src.core.models.user import User
from src.core.services.jwt_service import JWTService
from src.factory import bcrypt, db


@pytest.fixture(autouse=True)
def reset_limiter(app_with_db):
    with app_with_db.app_context():
        from src.factory import limiter

        limiter.reset()


@pytest.fixture
def test_user(session):
    """Create a test user with a known password for authentication testing"""
    email = "test@example.com"
    user = User.query.filter_by(email=email).first()

    if not user:
        password_hash = bcrypt.generate_password_hash("password123").decode("utf-8")
        user = User(email=email, password=password_hash)
        session.add(user)
        session.commit()

    return user


@pytest.fixture
def auth_header(test_user):
    """Generate a valid auth header for protected endpoints"""
    user_data = {"user_id": str(test_user.id), "email": test_user.email}
    access_token = JWTService.create_access_token(user_data)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def sample_strings(session):
    """Create sample strings in the database for testing retrieval"""
    strings = [
        "Hello, World!",
        "Testing 123",
        "Lorem ipsum dolor sit amet",
        "Flask API Test",
        "Python is awesome",
    ]

    for value in strings:
        string_obj = String(value=value)
        session.add(string_obj)

    session.commit()
    return strings


def generate_random_string(length=100):
    """Generate a random string of specified length"""
    return "".join(
        random.choices(
            string.ascii_letters + string.digits + string.punctuation + " ", k=length
        )
    )


class TestStringSave:
    """Tests for the string save endpoint"""

    def test_save_string_success(self, client, auth_header):
        """Test successfully saving a string"""
        test_string = "This is a test string"
        response = client.post(
            "/api/v1/strings/save",
            json={"string": test_string},
            headers=auth_header,
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.CREATED
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert "id" in data
        assert data["message"] == "String saved successfully"

        # Verify string was actually saved in database
        with client.application.app_context():
            saved_string = String.query.get(data["id"])
            assert saved_string is not None
            assert saved_string.value == test_string

    def test_save_string_unauthorized(self, client):
        """Test saving a string without authentication"""
        response = client.post(
            "/api/v1/strings/save",
            json={"string": "Test string"},
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        data = json.loads(response.data)
        assert data["status"] == "failed"
        assert "Missing authentication token" in data["message"]

    def test_save_string_invalid_token(self, client):
        """Test saving a string with invalid token"""
        response = client.post(
            "/api/v1/strings/save",
            json={"string": "Test string"},
            headers={"Authorization": "Bearer invalid.token.here"},
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        data = json.loads(response.data)
        assert data["status"] == "failed"

    def test_save_string_no_json(self, client, auth_header):
        """Test saving a string without JSON content"""
        response = client.post(
            "/api/v1/strings/save",
            data="This is not JSON",
            headers=auth_header,
            content_type="text/plain",
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = json.loads(response.data)
        assert data["status"] == "failed"
        assert "Request must be JSON" in data["message"]

    def test_save_empty_string(self, client, auth_header):
        """Test saving an empty string"""
        response = client.post(
            "/api/v1/strings/save",
            json={"string": ""},
            headers=auth_header,
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = json.loads(response.data)
        assert data["status"] == "failed"
        assert "validation error for StringCreateSchema" in data["message"]
        assert "at least 1 character" in data["message"]

    def test_save_non_string_value(self, client, auth_header):
        """Test saving a non-string value"""
        response = client.post(
            "/api/v1/strings/save",
            json={"string": 12345},
            headers=auth_header,
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = json.loads(response.data)
        assert data["status"] == "failed"
        assert "validation error for StringCreateSchema" in data["message"]
        assert "valid string" in data["message"]

    def test_save_missing_string_field(self, client, auth_header):
        """Test missing string field in request"""
        response = client.post(
            "/api/v1/strings/save",
            json={"not_string": "Test"},
            headers=auth_header,
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = json.loads(response.data)
        assert data["status"] == "failed"
        assert "validation error for StringCreateSchema" in data["message"]
        assert "Field required" in data["message"]

    def test_save_long_string(self, client, auth_header):
        """Test saving a very long string (just under the limit)"""
        long_string = generate_random_string(9999)
        response = client.post(
            "/api/v1/strings/save",
            json={"string": long_string},
            headers=auth_header,
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.CREATED
        data = json.loads(response.data)
        assert data["status"] == "success"

    def test_save_too_long_string(self, client, auth_header):
        """Test saving a string that exceeds the length limit"""
        too_long_string = generate_random_string(10500)
        response = client.post(
            "/api/v1/strings/save",
            json={"string": too_long_string},
            headers=auth_header,
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = json.loads(response.data)
        assert data["status"] == "failed"
        assert "validation error for StringCreateSchema" in data["message"]
        assert "at most 10000 characters" in data["message"]

    def test_save_special_characters(self, client, auth_header):
        """Test saving a string with special characters"""
        special_string = "!@#$%^&*()_+{}:\"|<>?[];',./`~"
        response = client.post(
            "/api/v1/strings/save",
            json={"string": special_string},
            headers=auth_header,
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.CREATED
        data = json.loads(response.data)
        assert data["status"] == "success"

        with client.application.app_context():
            saved_string = String.query.get(data["id"])
            assert saved_string.value == special_string

    def test_save_empty_json(self, client, auth_header):
        """Test saving with empty JSON"""
        response = client.post(
            "/api/v1/strings/save",
            json={},
            headers=auth_header,
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = json.loads(response.data)
        assert data["status"] == "failed"
        assert "validation error for StringCreateSchema" in data["message"]
        assert "Field required" in data["message"]

    def test_save_string_expired_token(self, client, auth_header):
        """Test saving with an expired token"""
        with patch(
            "src.core.services.jwt_service.JWTService.decode_token"
        ) as mock_decode:
            mock_decode.side_effect = ValueError("Token has expired")

            response = client.post(
                "/api/v1/strings/save",
                json={"string": "Test string"},
                headers=auth_header,
                content_type="application/json",
            )

            assert response.status_code == HTTPStatus.UNAUTHORIZED
            data = json.loads(response.data)
            assert data["status"] == "failed"
            assert "Token has expired" in data["message"]

    def test_save_multiple_strings_sequentially(self, client, auth_header):
        """Test saving multiple strings in sequence"""
        strings = ["First string", "Second string", "Third string"]
        ids = []

        for test_string in strings:
            response = client.post(
                "/api/v1/strings/save",
                json={"string": test_string},
                headers=auth_header,
                content_type="application/json",
            )

            assert response.status_code == HTTPStatus.CREATED
            data = json.loads(response.data)
            ids.append(data["id"])

        with client.application.app_context():
            for i, string_id in enumerate(ids):
                saved_string = String.query.get(string_id)
                assert saved_string.value == strings[i]


class TestRandomString:
    """Tests for the random string endpoint"""

    def test_get_random_string_success(self, client, session, sample_strings):
        """Test successfully retrieving a random string"""
        session.query(String).delete()
        session.commit()

        for value in sample_strings:
            string_obj = String(value=value)
            session.add(string_obj)
        session.commit()

        response = client.get("/api/v1/strings/random")

        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.data)
        assert "random_string" in data
        assert data["random_string"] in sample_strings

    def test_get_random_string_empty_db(self, client):
        """Test retrieving a random string when database is empty"""
        # Ensure database is empty
        with client.application.app_context():
            db.session.query(String).delete()
            db.session.commit()

        response = client.get("/api/v1/strings/random")

        assert response.status_code == HTTPStatus.NOT_FOUND
        data = json.loads(response.data)
        assert "message" in data
        assert "No strings found" in data["message"]

    def test_random_string_no_auth_required(self, client, sample_strings):
        """Verify random string endpoint doesn't require authentication"""
        response = client.get(
            "/api/v1/strings/random",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.data)
        assert "random_string" in data
        assert data["random_string"] in sample_strings

    def test_rate_limiting(self, client, sample_strings):
        """Test that rate limiting is applied to the random endpoint"""
        responses = []
        for _ in range(150):
            response = client.get("/api/v1/strings/random")
            responses.append(response)
            if response.status_code == 429:
                break

        assert any(
            r.status_code == HTTPStatus.TOO_MANY_REQUESTS for r in responses
        ), "Rate limiting was not triggered"


class TestIntegration:
    """Integration tests that combine multiple operations"""

    def test_save_and_retrieve(self, client, auth_header):
        """Test saving a string and then retrieving it randomly"""
        with client.application.app_context():
            db.session.query(String).delete()
            db.session.commit()

        unique_string = f"Unique test string {random.randint(1000, 9999)}"
        save_response = client.post(
            "/api/v1/strings/save",
            json={"string": unique_string},
            headers=auth_header,
            content_type="application/json",
        )

        assert save_response.status_code == HTTPStatus.CREATED

        get_response = client.get("/api/v1/strings/random")

        assert get_response.status_code == HTTPStatus.OK
        data = json.loads(get_response.data)
        assert data["random_string"] == unique_string

    def test_concurrent_saves(self, client, auth_header):
        """Test saving multiple strings with different content"""
        test_strings = [
            "String A: " + generate_random_string(10),
            "String B: " + generate_random_string(10),
            "String C: " + generate_random_string(10),
        ]

        responses = []
        for test_string in test_strings:
            response = client.post(
                "/api/v1/strings/save",
                json={"string": test_string},
                headers=auth_header,
                content_type="application/json",
            )
            responses.append(response)

        for response in responses:
            assert response.status_code == HTTPStatus.CREATED

        with client.application.app_context():
            for test_string in test_strings:
                saved = String.query.filter_by(value=test_string).first()
                assert saved is not None
