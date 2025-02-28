import json


def test_swagger_endpoint_available(client):
    """Test that the swagger.json endpoint is accessible"""
    response = client.get("/api/v1/swagger.json")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_swagger_content_validity(client):
    """Test that swagger.json contains all required endpoints"""
    response = client.get("/api/v1/swagger.json")
    data = json.loads(response.data)

    # Check OpenAPI structure
    assert "openapi" in data
    assert "paths" in data
    assert "components" in data
    assert "schemas" in data["components"]

    # Check all endpoints are documented
    assert "/strings/save" in data["paths"]
    assert "/strings/random" in data["paths"]
    assert "/auth/login" in data["paths"]
    assert "/auth/register" in data["paths"]
    assert "/auth/refresh" in data["paths"]

    # Check auth endpoints have proper request bodies
    assert "requestBody" in data["paths"]["/auth/login"]["post"]
    assert "requestBody" in data["paths"]["/auth/register"]["post"]
    assert "requestBody" in data["paths"]["/auth/refresh"]["post"]

    # Check string endpoints have proper schemas
    assert "/strings/save" in data["paths"]
    assert "post" in data["paths"]["/strings/save"]
    assert "security" in data["paths"]["/strings/save"]["post"]

    # Check component schemas exist
    schemas = data["components"]["schemas"]
    required_schemas = [
        "StringCreate",
        "StringCreateResponse",
        "RandomStringResponse",
        "LoginRequest",
        "RegisterRequest",
        "TokenResponse",
        "RefreshTokenRequest",
        "ErrorResponse",
    ]
    for schema in required_schemas:
        assert schema in schemas


def test_docs_ui_accessible(client):
    """Test that Swagger UI is accessible"""
    response = client.get("/docs/")
    assert response.status_code == 200
    assert b"swagger-ui" in response.data
