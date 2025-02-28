import json
from http import HTTPStatus
from unittest.mock import patch

import pytest

from src.core.models.user import User
from src.core.services.jwt_service import JWTService
from src.factory import bcrypt, db


@pytest.fixture
def test_user(session):  # Use the session fixture instead of app_with_db
    email = "test@example.com"
    user = User.query.filter_by(email=email).first()

    if not user:
        password_hash = bcrypt.generate_password_hash("password123").decode("utf-8")
        user = User(email=email, password=password_hash)
        session.add(user)
        session.commit()

    return user


@pytest.fixture
def auth_tokens(app_with_db, test_user):
    with app_with_db.app_context():
        user_data = {"user_id": str(test_user.id), "email": test_user.email}
        access_token = JWTService.create_access_token(user_data)
        refresh_token = JWTService.create_refresh_token(user_data)

        return {"access": access_token, "refresh": refresh_token}


def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "securepassword123"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.CREATED
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert "access_token" in data
    assert "refresh_token" in data

    with client.application.app_context():
        user = User.query.filter_by(email="newuser@example.com").first()
        assert user is not None


def test_register_email_exists(client, session):
    email = "test@example.com"
    password_hash = bcrypt.generate_password_hash("password123").decode("utf-8")
    user = User(email=email, password=password_hash)
    session.add(user)
    session.commit()

    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.CONFLICT
    data = json.loads(response.data)
    assert data["status"] == "failed"
    assert "Email already registered" in data["message"]


def test_register_invalid_json(client):
    response = client.post(
        "/api/v1/auth/register", data="not a json", content_type="text/plain"
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = json.loads(response.data)
    assert data["status"] == "failed"
    assert "Request must be JSON" in data["message"]


def test_register_missing_fields(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = json.loads(response.data)

    assert data["status"] == "failed"
    assert "validation error for RegisterRequestSchema" in data["message"]
    assert "password" in data["message"]


def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "password123"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "wrongpassword"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = json.loads(response.data)
    assert data["status"] == "failed"
    assert "Invalid email or password" in data["message"]


def test_login_user_not_found(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "password123"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = json.loads(response.data)
    assert data["status"] == "failed"


def test_refresh_token_missing(client):
    response = client.post(
        "/api/v1/auth/refresh", json={}, content_type="application/json"
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = json.loads(response.data)
    assert data["status"] == "failed"
    assert "validation error for RefreshTokenRequestSchema" in data["message"]
    assert "refresh_token" in data["message"]
    assert "Field required" in data["message"]


def test_refresh_token_invalid(client):
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = json.loads(response.data)
    assert data["status"] == "failed"


def test_protected_endpoint_with_valid_token(client, auth_tokens):
    response = client.post(
        "/api/v1/strings/save",
        json={"string": "Test string"},
        headers={"Authorization": f"Bearer {auth_tokens['access']}"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.CREATED
    data = json.loads(response.data)
    assert data["status"] == "success"


def test_protected_endpoint_without_token(client):
    response = client.post(
        "/api/v1/strings/save",
        json={"string": "Test string"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = json.loads(response.data)
    assert data["status"] == "failed"
    assert "Missing authentication token" in data["message"]


def test_protected_endpoint_with_invalid_token(client):
    response = client.post(
        "/api/v1/strings/save",
        json={"string": "Test string"},
        headers={"Authorization": "Bearer invalid.token.here"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = json.loads(response.data)
    assert data["status"] == "failed"


def test_protected_endpoint_with_refresh_token(client, auth_tokens):
    response = client.post(
        "/api/v1/strings/save",
        json={"string": "Test string"},
        headers={"Authorization": f"Bearer {auth_tokens['refresh']}"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = json.loads(response.data)
    assert data["status"] == "failed"
    assert "Invalid token type" in data["message"]


@patch("src.core.services.jwt_service.JWTService.decode_token")
def test_expired_token(mock_decode, client, auth_tokens):
    mock_decode.side_effect = ValueError("Token has expired")

    response = client.post(
        "/api/v1/strings/save",
        json={"string": "Test string"},
        headers={"Authorization": f"Bearer {auth_tokens['access']}"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = json.loads(response.data)
    assert data["status"] == "failed"
    assert "Token has expired" in data["message"]


def test_rate_limiting_on_login(client):
    for i in range(15):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "anypassword"},
            content_type="application/json",
        )
        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            break

    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS


def test_rate_limiting_on_register(client):
    for i in range(15):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": f"user{i}@example.com", "password": "password123"},
            content_type="application/json",
        )
        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            break

    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS


def test_malformed_authorization_header(client):
    response = client.post(
        "/api/v1/strings/save",
        json={"string": "Test string"},
        headers={"Authorization": "malformed-header"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = json.loads(response.data)
    assert data["status"] == "failed"
