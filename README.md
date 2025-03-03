# Testing the App

For installation please refer to the [INSTALLATION.md](INSTALLATION.md) file.

For detailed docs refer to the [docs](http://flask-api.local:5000/docs/) url.

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

# Monitoring and Logs

For monitoring and logs please refer to the [monitoring-and-logs.md](docs/monitoring-and-logs.md) file.

# Running Tests

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
