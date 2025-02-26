from flask import Blueprint, jsonify, render_template_string
from flask_swagger_ui import get_swaggerui_blueprint

# Create swagger blueprint
swagger = Blueprint("swagger", __name__)

# Set up Swagger UI
SWAGGER_URL = "/docs"
API_URL = "/api/v1/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Flask String API"}
)


# Define API documentation
@swagger.route("/swagger.json")
def swagger_json():
    swagger_doc = {
        "openapi": "3.0.0",
        "info": {
            "title": "Flask String API",
            "description": "API for storing and retrieving random strings",
            "version": "1.0.0",
        },
        "servers": [{"url": "/api/v1", "description": "API v1"}],
        "paths": {
            "/strings/save": {
                "post": {
                    "summary": "Save a string",
                    "description": "Save a string to the database",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "string": {
                                            "type": "string",
                                            "description": "String to save",
                                        }
                                    },
                                    "required": ["string"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "String saved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"},
                                            "status": {"type": "string"},
                                            "id": {"type": "integer"},
                                        },
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Bad request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {"type": "string"},
                                            "status": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "500": {"description": "Internal server error"},
                    },
                }
            },
            "/strings/random": {
                "get": {
                    "summary": "Get a random string",
                    "description": "Retrieve a random string from the database",
                    "responses": {
                        "200": {
                            "description": "A random string",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "random_string": {"type": "string"}
                                        },
                                    }
                                }
                            },
                        },
                        "404": {"description": "No strings found"},
                        "500": {"description": "Internal server error"},
                    },
                }
            },
        },
    }
    return jsonify(swagger_doc)


def register_swagger(app):
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    app.register_blueprint(swagger, url_prefix="/api/v1")
