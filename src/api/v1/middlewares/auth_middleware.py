from functools import wraps
from http import HTTPStatus

from flask import request
from pydantic import ValidationError

from src.core.schemas.auth import TokenPayloadSchema
from src.core.services.jwt_service import JWTService
from src.utils import create_error_response


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
            return create_error_response(
                "Missing authentication token", HTTPStatus.UNAUTHORIZED
            )

        try:
            # Decode and validate token
            payload = JWTService.decode_token(token)

            # Validate payload structure with Pydantic
            try:
                token_data = TokenPayloadSchema(**payload)
            except ValidationError:
                return create_error_response(
                    "Invalid token structure", HTTPStatus.UNAUTHORIZED
                )

            # Check token type
            if token_data.type != "access":
                return create_error_response(
                    "Invalid token type", HTTPStatus.UNAUTHORIZED
                )

            # Add user info to request
            request.current_user = {
                "user_id": token_data.user_id,
                "email": token_data.email,
            }

            return f(*args, **kwargs)

        except ValueError as e:
            return create_error_response(str(e), HTTPStatus.UNAUTHORIZED)
        except Exception:
            return create_error_response(
                "Invalid authentication token", HTTPStatus.UNAUTHORIZED
            )

    return decorated
