# Testing the App

For installation please refer to the [INSTALLATION.md](INSTALLATION.md) file.

For OpenAPI docs refer to the `http://flask-api.local/docs` url once the
app running.

## Auth Endpoints

### Register a new user
```bash
curl -X POST http://flask-api.local/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### Login with existing user
```bash
curl -X POST http://flask-api.local/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### Refresh token

Replace with actual refresh token from login response

```bash
curl -X POST http://flask-api.local/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

## String Endpoints

### Save a string (protected - requires token from login response)

```bash
curl -X POST http://flask-api.local/api/v1/strings/save \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "string": "Hello, this is a test string!"
  }'
```

### Get a random string (public endpoint - no auth required)

```bash
curl -X GET http://flask-api.local/api/v1/strings/random
```

# Monitoring and Logs

For monitoring and logs please refer to the [monitoring-and-logs.md](docs/monitoring-and-logs.md) file.

# Running Tests

You can also install the dependencies and run the tests without starting
the cluster.

```bash
pyhon -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the tests:

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
