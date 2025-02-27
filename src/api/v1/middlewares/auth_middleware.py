from functools import wraps
from http import HTTPStatus

from flask import Response, json, request

from src.core.services.jwt_service import JWTService


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Missing authentication token"}
                ),
                status=HTTPStatus.UNAUTHORIZED,
                mimetype="application/json",
            )

        try:
            # Decode and validate token
            payload = JWTService.decode_token(token)

            # Check token type
            if payload.get("type") != "access":
                return Response(
                    response=json.dumps(
                        {"status": "error", "message": "Invalid token type"}
                    ),
                    status=HTTPStatus.UNAUTHORIZED,
                    mimetype="application/json",
                )

            # Add user info to request
            request.current_user = {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
            }

            return f(*args, **kwargs)

        except ValueError as e:
            return Response(
                response=json.dumps({"status": "error", "message": str(e)}),
                status=HTTPStatus.UNAUTHORIZED,
                mimetype="application/json",
            )
        except Exception:
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Invalid authentication token"}
                ),
                status=HTTPStatus.UNAUTHORIZED,
                mimetype="application/json",
            )

    return decorated
