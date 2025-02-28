# Testing the App

For installation please refer to the [INSTALLATION.md](INSTALLATION.md) file.

## Auth Endpoints

### Register a new user
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### Login with existing user
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### Refresh token

Replace with actual refresh token from login response

```bash
curl -X POST http://localhost:5000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

## String Endpoints

### Save a string (protected - requires token from login response)

```bash
curl -X POST http://localhost:5000/api/v1/strings/save \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "string": "Hello, this is a test string!"
  }'
```

### Get a random string (public endpoint - no auth required)

```bash
curl -X GET http://localhost:5000/api/v1/strings/random
```

# Running Tests

1. Set the environment to "test":

```bash
export ENV=test
```

2. Run the tests using pytest:

```bash
pytest
```

You can also run specific test files:

```bash
pytest tests/test_strings.py
pytest tests/test_auth.py
```

Or specific test functions:

```bash
pytest tests/test_strings.py::test_save_string
```

## How It Works

- When the ENV environment variable is set to "test", the application uses
TestConfig
- TestConfig configures SQLAlchemy to use an in-memory SQLite database
- The test fixtures in conftest.py create and tear down the database for each
test
- Each test runs in its own transaction that is rolled back after the test is
complete

## Database Fixtures

The following fixtures are available for your tests:

- `app_with_db`: The Flask application configured with an in-memory database
- `client`: A Flask test client for making HTTP requests
- `session`: A SQLAlchemy session for direct database access

## Example Usage

```python
def test_my_endpoint(client, session):
    # Create test data directly in the database
    new_item = MyModel(name="Test Item")
    session.add(new_item)
    session.commit()
    
    # Make HTTP request
    response = client.get("/api/v1/my-endpoint")
    
    # Assert response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Test Item"
```

## Production Configuration

This setup is for testing only. The application will continue to use MySQL in
development and production environments.
