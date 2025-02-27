import pytest
from flask import Flask
from src.core.security import configure_security

@pytest.fixture
def app():
    app = Flask(__name__)
    configure_security(app)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_security_headers(client, base_url):
    """Test that security headers are properly set"""
    response = client.get(f'/health')  # No need for base_url with test client
    
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['Strict-Transport-Security'] == 'max-age=31536000; includeSubDomains'
    assert response.headers['Cache-Control'] == 'no-store, no-cache, must-revalidate, max-age=0'

def test_request_size_limit(client, base_url):
    """Test request size limitation"""
    large_data = {'string': 'x' * (1024 * 1024 + 1)}  # Exceeds 1MB
    response = client.post('/api/v1/strings/save', json=large_data)
    assert response.status_code == 413
    assert b'Request too large' in response.data

def test_content_type_validation(client, base_url):
    """Test content type validation"""
    response = client.post('/api/v1/strings/save', 
                         data='not-json',
                         content_type='text/plain')
    assert response.status_code == 400
    assert b'Content-Type must be application/json' in response.data

def test_rate_limiting(client, base_url):
    """Test rate limiting"""
    # Test signin endpoint rate limit (5 per minute)
    for i in range(6):
        response = client.post('/api/v1/auth/signin')
    assert response.status_code == 429  # Too Many Requests
