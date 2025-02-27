from http import HTTPStatus

from flask import Flask, request


def configure_security(app: Flask):
    @app.after_request
    def add_security_headers(response):
        # Prevents MIME-sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Strict transport security for HTTPS
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        # Cache control for API responses
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        return response

    @app.before_request
    def validate_request():
        if request.is_json:
            if not request.content_type == "application/json":
                return {
                    "error": "Content-Type must be application/json"
                }, HTTPStatus.BAD_REQUEST
            if request.content_length > 1024 * 1024:  # 1MB limit
                return {
                    "error": "Request too large"
                }, HTTPStatus.REQUEST_ENTITY_TOO_LARGE
