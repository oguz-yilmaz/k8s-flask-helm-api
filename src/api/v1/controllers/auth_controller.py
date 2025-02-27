import logging
from http import HTTPStatus

from flask import Blueprint, Response, json, request

from src.core.models.user import User
from src.core.services.jwt_service import JWTService
from src.factory import bcrypt, db, limiter

auth = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


@limiter.limit("10 per minute")
@auth.route("/login", methods=["POST"])
def handle_login():
    try:
        # Validate request data
        if not request.is_json:
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Request must be JSON"}
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

        data = request.json
        if not all(k in data for k in ["email", "password"]):
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Email and password are required"}
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

        user = User.query.filter_by(email=data["email"]).first()

        # Validate credentials
        if not user or not bcrypt.check_password_hash(user.password, data["password"]):
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Invalid email or password"}
                ),
                status=HTTPStatus.UNAUTHORIZED,
                mimetype="application/json",
            )

        # Generate tokens
        user_data = {"user_id": str(user.id), "email": user.email}
        access_token = JWTService.create_access_token(user_data)
        refresh_token = JWTService.create_refresh_token(user_data)

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                }
            ),
            status=HTTPStatus.OK,
            mimetype="application/json",
        )

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return Response(
            response=json.dumps(
                {"status": "error", "message": "Authentication failed"}
            ),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )


@limiter.limit("10 per minute")
@auth.route("/register", methods=["POST"])
def handle_register():
    try:
        # Validate request
        if not request.is_json:
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Request must be JSON"}
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

        data = request.json
        if not all(k in data for k in ["email", "password"]):
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Email and password are required"}
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

        # Check if user exists
        if User.query.filter_by(email=data["email"]).first():
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Email already registered"}
                ),
                status=HTTPStatus.CONFLICT,
                mimetype="application/json",
            )

        # Create user
        password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
        user = User(email=data["email"], password=password_hash)
        db.session.add(user)
        db.session.commit()

        # Generate tokens
        user_data = {"user_id": str(user.id), "email": user.email}
        access_token = JWTService.create_access_token(user_data)
        refresh_token = JWTService.create_refresh_token(user_data)

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Registration successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                }
            ),
            status=HTTPStatus.CREATED,
            mimetype="application/json",
        )

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return Response(
            response=json.dumps({"status": "error", "message": "Registration failed"}),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )


@limiter.limit("10 per minute")
@auth.route("/refresh", methods=["POST"])
def refresh_token():
    try:
        if not request.is_json:
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Request must be JSON"}
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

        data = request.json
        if "refresh_token" not in data:
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Refresh token is required"}
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

        # Validate refresh token
        try:
            payload = JWTService.decode_refresh_token(data["refresh_token"])
        except ValueError as e:
            return Response(
                response=json.dumps({"status": "error", "message": str(e)}),
                status=HTTPStatus.UNAUTHORIZED,
                mimetype="application/json",
            )

        # Check if user exists
        user = User.query.filter_by(id=payload["user_id"]).first()
        if not user:
            return Response(
                response=json.dumps({"status": "error", "message": "User not found"}),
                status=HTTPStatus.UNAUTHORIZED,
                mimetype="application/json",
            )

        # Generate new access token
        user_data = {"user_id": str(user.id), "email": user.email}
        access_token = JWTService.create_access_token(user_data)

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Token refreshed successfully",
                    "access_token": access_token,
                    "token_type": "bearer",
                }
            ),
            status=HTTPStatus.OK,
            mimetype="application/json",
        )

    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        return Response(
            response=json.dumps({"status": "error", "message": "Token refresh failed"}),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )
