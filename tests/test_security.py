from http import HTTPStatus

import pytest
from flask import Flask

from src.core.security import configure_security


def test_security_headers(client):
    """Test that security headers are properly set"""
    response = client.get(f"/health")  # No need for base_url with test client

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert (
        response.headers["Strict-Transport-Security"]
        == "max-age=31536000; includeSubDomains"
    )
    assert (
        response.headers["Cache-Control"]
        == "no-store, no-cache, must-revalidate, max-age=0"
    )


def test_request_size_limit(client):
    """Test request size limitation"""
    large_data = {"string": "x" * (1024 * 1024 + 1)}  # Exceeds 1MB
    response = client.post("/api/v1/strings/save", json=large_data)
    assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    assert b"Request too large" in response.data


def test_content_type_validation(client):
    """Test content type validation"""
    response = client.post(
        "/api/v1/strings/save", data="not-json", content_type="text/plain"
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b'{"error": "Request must be JSON", "status": "failed"}' in response.data


def test_rate_limiting(client):
    """Test rate limiting (100 requests per minute)"""

    # Make a valid request first to ensure the endpoint works properly
    response = client.post(
        "/api/v1/auth/signin",
        json={"email": "test@example.com", "password": "password"},
        content_type="application/json",
    )

    # Check status before we hit rate limit
    assert (
        response.status_code != 500
    ), f"Initial request failed with error: {response.data}"

    # Now make requests until we hit the rate limit
    # We'll use fewer requests (101 instead of 105) to save time
    for i in range(101):
        response = client.post(
            "/api/v1/auth/signin",
            json={"email": "test@example.com", "password": "password"},
            content_type="application/json",
        )

        # If we get a 429 response, the test is successful
        if response.status_code == 429:
            break

    # Verify that we eventually got rate limited
    assert (
        response.status_code == 429
    ), f"Expected rate limit (429) but got {response.status_code}"
