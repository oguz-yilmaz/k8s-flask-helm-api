from flask import Blueprint, jsonify, render_template_string
from flask_swagger_ui import get_swaggerui_blueprint

swagger = Blueprint("swagger", __name__)

SWAGGER_URL = "/docs"
API_URL = "/api/v1/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Flask String API"}
)


@swagger.route("/swagger.json")
def swagger_json():
    swagger_doc = {
        "openapi": "3.0.0",
        "info": {
            "title": "Flask String API",
            "description": "API for storing and retrieving random strings with authentication",
            "version": "1.0.0",
        },
        "servers": [{"url": "/api/v1", "description": "API v1"}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            },
            "schemas": {
                "StringCreate": {
                    "type": "object",
                    "properties": {
                        "string": {
                            "type": "string",
                            "description": "String to save",
                            "minLength": 1,
                            "maxLength": 10000,
                        }
                    },
                    "required": ["string"],
                },
                "StringCreateResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "message": {
                            "type": "string",
                            "example": "String saved successfully",
                        },
                        "id": {"type": "integer", "example": 1},
                    },
                },
                "RandomStringResponse": {
                    "type": "object",
                    "properties": {
                        "random_string": {
                            "type": "string",
                            "example": "This is a randomly selected string",
                        }
                    },
                },
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "failed"},
                        "message": {"type": "string", "example": "Error message"},
                        "error_code": {"type": "string", "example": "INVALID_REQUEST"},
                    },
                },
                "LoginRequest": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "format": "email",
                            "example": "user@example.com",
                        },
                        "password": {
                            "type": "string",
                            "format": "password",
                            "example": "secure-password-123",
                            "minLength": 8,
                        },
                    },
                    "required": ["email", "password"],
                },
                "RegisterRequest": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "format": "email",
                            "example": "user@example.com",
                        },
                        "password": {
                            "type": "string",
                            "format": "password",
                            "example": "secure-password-123",
                            "minLength": 8,
                        },
                    },
                    "required": ["email", "password"],
                },
                "TokenResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "message": {"type": "string", "example": "Login successful"},
                        "access_token": {
                            "type": "string",
                            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        },
                        "refresh_token": {
                            "type": "string",
                            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        },
                        "token_type": {"type": "string", "example": "bearer"},
                    },
                },
                "RefreshTokenRequest": {
                    "type": "object",
                    "properties": {
                        "refresh_token": {
                            "type": "string",
                            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        }
                    },
                    "required": ["refresh_token"],
                },
            },
        },
        "paths": {
            "/strings/save": {
                "post": {
                    "summary": "Save a string",
                    "description": "Save a string to the database (requires authentication)",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StringCreate"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "String saved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/StringCreateResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Bad request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "401": {
                            "description": "Unauthorized",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "429": {
                            "description": "Too many requests",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                    },
                }
            },
            "/strings/random": {
                "get": {
                    "summary": "Get a random string",
                    "description": "Retrieve a random string from the database (public endpoint)",
                    "responses": {
                        "200": {
                            "description": "A random string",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/RandomStringResponse"
                                    }
                                }
                            },
                        },
                        "404": {
                            "description": "No strings found",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "429": {
                            "description": "Too many requests",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                    },
                }
            },
            "/auth/register": {
                "post": {
                    "summary": "Register a new user",
                    "description": "Create a new user account and get authentication tokens",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/RegisterRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Registration successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TokenResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Bad request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "409": {
                            "description": "Conflict - Email already exists",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "429": {
                            "description": "Too many requests",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                    },
                }
            },
            "/auth/login": {
                "post": {
                    "summary": "User login",
                    "description": "Authenticate and get access and refresh tokens",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/LoginRequest"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Login successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TokenResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Bad request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "401": {
                            "description": "Invalid credentials",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "429": {
                            "description": "Too many requests",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                    },
                }
            },
            "/auth/refresh": {
                "post": {
                    "summary": "Refresh access token",
                    "description": "Get a new access token using a valid refresh token",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/RefreshTokenRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Token refresh successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TokenResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Bad request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "401": {
                            "description": "Invalid refresh token",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "429": {
                            "description": "Too many requests",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                    },
                }
            },
        },
    }
    return jsonify(swagger_doc)


def register_swagger(app):
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    app.register_blueprint(swagger, url_prefix="/api/v1")
