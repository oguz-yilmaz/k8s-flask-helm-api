from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def configure_security(app: Flask):
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    limiter.limit("5 per minute")(app.route("/api/v1/auth/signin"))
    limiter.limit("3 per minute")(app.route("/api/v1/auth/signup"))
    limiter.limit("100 per minute")(app.route("/api/v1/strings/save"))

    @app.after_request
    def add_security_headers(response):
        # Prevents MIME-sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Strict transport security for HTTPS
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        # Cache control for API responses
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response

    @app.before_request
    def validate_request():
        if request.is_json:
            if not request.content_type == 'application/json':
                return {'error': 'Content-Type must be application/json'}, 400
            if request.content_length > 1024 * 1024:  # 1MB limit
                return {'error': 'Request too large'}, 413