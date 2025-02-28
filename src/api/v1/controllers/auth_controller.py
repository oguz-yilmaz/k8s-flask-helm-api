import logging
from http import HTTPStatus

from flask import Blueprint, request
from pydantic import ValidationError

from src.core.models.user import User
from src.core.schemas.auth import (
    LoginRequestSchema,
    RefreshTokenRequestSchema,
    RegisterRequestSchema,
    TokenPayloadSchema,
    TokenResponseSchema,
)
from src.core.services.jwt_service import JWTService
from src.factory import bcrypt, db, limiter
from src.utils import create_error_response, create_success_response

auth = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


@auth.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def handle_login():
    try:
        # Validate request format
        if not request.is_json:
            return create_error_response("Request must be JSON", HTTPStatus.BAD_REQUEST)

        # Validate request data with Pydantic
        try:
            login_data = LoginRequestSchema(**request.json)
        except ValidationError as e:
            return create_error_response(
                f"Validation error: {e}", HTTPStatus.BAD_REQUEST
            )

        user = User.query.filter_by(email=login_data.email).first()

        # Validate credentials
        if not user or not bcrypt.check_password_hash(
            user.password, login_data.password
        ):
            return create_error_response(
                "Invalid email or password", HTTPStatus.UNAUTHORIZED
            )

        # Generate tokens
        user_data = {"user_id": str(user.id), "email": user.email}
        access_token = JWTService.create_access_token(user_data)
        refresh_token = JWTService.create_refresh_token(user_data)

        # Create response using Pydantic schema
        token_response = TokenResponseSchema(
            message="Login successful",
            access_token=access_token,
            refresh_token=refresh_token,
        )

        return create_success_response(token_response.model_dump(), HTTPStatus.OK)

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return create_error_response(
            "Authentication failed", HTTPStatus.INTERNAL_SERVER_ERROR
        )


@auth.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def handle_register():
    try:
        # Validate request format
        if not request.is_json:
            return create_error_response("Request must be JSON", HTTPStatus.BAD_REQUEST)

        # Validate request data with Pydantic
        try:
            register_data = RegisterRequestSchema(**request.json)
        except ValidationError as e:
            return create_error_response(
                f"Validation error: {e}", HTTPStatus.BAD_REQUEST
            )

        # Check if user exists
        if User.query.filter_by(email=register_data.email).first():
            return create_error_response(
                "Email already registered", HTTPStatus.CONFLICT
            )

        # Create user
        password_hash = bcrypt.generate_password_hash(register_data.password).decode(
            "utf-8"
        )
        user = User(email=register_data.email, password=password_hash)
        db.session.add(user)
        db.session.commit()

        # Generate tokens
        user_data = {"user_id": str(user.id), "email": user.email}
        access_token = JWTService.create_access_token(user_data)
        refresh_token = JWTService.create_refresh_token(user_data)

        # Create response using Pydantic schema
        token_response = TokenResponseSchema(
            message="Registration successful",
            access_token=access_token,
            refresh_token=refresh_token,
        )

        return create_success_response(token_response.model_dump(), HTTPStatus.CREATED)

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        db.session.rollback()
        return create_error_response(
            "Registration failed", HTTPStatus.INTERNAL_SERVER_ERROR
        )


@limiter.limit("10 per minute")
@auth.route("/refresh", methods=["POST"])
def refresh_token():
    try:
        # Validate request format
        if not request.is_json:
            return create_error_response("Request must be JSON", HTTPStatus.BAD_REQUEST)

        # Validate request data with Pydantic
        try:
            refresh_data = RefreshTokenRequestSchema(**request.json)
        except ValidationError as e:
            return create_error_response(
                f"Validation error: {e}", HTTPStatus.BAD_REQUEST
            )

        # Validate refresh token
        try:
            payload = JWTService.decode_refresh_token(refresh_data.refresh_token)
            # Validate payload structure with Pydantic
            TokenPayloadSchema(**payload)
        except (ValueError, ValidationError) as e:
            return create_error_response(str(e), HTTPStatus.UNAUTHORIZED)

        # Check if user exists
        user = User.query.filter_by(id=payload["user_id"]).first()
        if not user:
            return create_error_response("User not found", HTTPStatus.UNAUTHORIZED)

        # Generate new access token
        user_data = {"user_id": str(user.id), "email": user.email}
        access_token = JWTService.create_access_token(user_data)

        # Create response using Pydantic schema
        token_response = TokenResponseSchema(
            message="Token refreshed successfully",
            access_token=access_token,
            refresh_token=None,  # Don't generate new refresh token
        )

        return create_success_response(token_response.model_dump(), HTTPStatus.OK)

    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        return create_error_response(
            "Token refresh failed", HTTPStatus.INTERNAL_SERVER_ERROR
        )
