from http import HTTPStatus

import pytest
from flask import Flask

from src.core.models.user import User
from src.core.security import configure_security


@pytest.fixture
def auth_token(app_with_db, client):
    """Create a test user and return a valid auth token"""
    from src.core.services.jwt_service import JWTService
    from src.factory import bcrypt

    # Create a test user
    with app_with_db.app_context():
        email = "test@example.com"
        user = User.query.filter_by(email=email).first()

        if not user:
            password_hash = bcrypt.generate_password_hash("password123").decode("utf-8")
            user = User(email=email, password=password_hash)
            from src.factory import db

            db.session.add(user)
            db.session.commit()

        user_data = {"user_id": str(user.id), "email": user.email}
        token = JWTService.create_access_token(user_data)

        return token


def test_security_headers(client):
    """Test that security headers are properly set"""
    response = client.get("/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert (
        response.headers["Strict-Transport-Security"]
        == "max-age=31536000; includeSubDomains"
    )
    assert (
        response.headers["Cache-Control"]
        == "no-store, no-cache, must-revalidate, max-age=0"
    )


def test_request_size_limit(client, auth_token):
    """Test request size limitation"""
    large_data = {"string": "x" * (1024 * 1024 + 1)}  # Exceeds 1MB

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    response = client.post("/api/v1/strings/save", json=large_data, headers=headers)
    assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    assert b"Request too large" in response.data


def test_content_type_validation(client, app_with_db):
    """Test content type validation"""
    with app_with_db.app_context():
        from src.factory import limiter

        limiter.reset()

        response = client.post(
            "/api/v1/auth/login", data="not-json", content_type="text/plain"
        )

        assert response.status_code == 400
        assert b"Request must be JSON" in response.data


def test_rate_limiting(client):
    """Test rate limiting"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password"},
        content_type="application/json",
    )

    assert (
        response.status_code != HTTPStatus.INTERNAL_SERVER_ERROR
    ), f"Initial request failed with error: {response.data}"

    # Make requests until we hit the rate limit
    for i in range(105):
        response = client.get("/api/v1/strings/random")

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            break

    assert (
        response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    ), f"Expected rate limit (429) but got {response.status_code}"
