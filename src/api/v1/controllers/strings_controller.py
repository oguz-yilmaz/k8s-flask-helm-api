import logging
import random
from http import HTTPStatus

from flask import Blueprint, Response, json, request

from src.api.v1 import db
from src.core.models.string import String

strings = Blueprint("strings", __name__)
logger = logging.getLogger(__name__)


@strings.route("/save", methods=["POST"])
def save_string():
    try:
        # Check if request has valid JSON
        if not request.is_json:
            return Response(
                response=json.dumps(
                    {"error": "Request must be JSON", "status": "failed"}
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

        data = request.get_json()

        # Check for null or missing string data
        if not data or "string" not in data:
            return Response(
                response=json.dumps(
                    {"error": "No string provided", "status": "failed"}
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

        input_string = data["string"]

        # Check if string is empty or too long
        if not input_string or not isinstance(input_string, str):
            return Response(
                response=json.dumps(
                    {"error": "Invalid string format", "status": "failed"}
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

        if len(input_string) > 10000:  # Set a reasonable limit
            return Response(
                response=json.dumps(
                    {"error": "String exceeds maximum length", "status": "failed"}
                ),
                status=HTTPStatus.BAD_REQUEST,
                mimetype="application/json",
            )

        # Create a new String object
        new_string = String(value=input_string)
        db.session.add(new_string)
        db.session.commit()

        return Response(
            response=json.dumps(
                {
                    "message": "String saved successfully",
                    "status": "success",
                    "id": new_string.id,
                }
            ),
            status=HTTPStatus.CREATED,
            mimetype="application/json",
        )

    except Exception as e:
        # Rollback the session in case of error
        db.session.rollback()
        logger.error(f"Error saving string: {e}")
        return Response(
            response=json.dumps({"error": "Internal server error", "status": "failed"}),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )


@strings.route("/random", methods=["GET"])
def get_random_string():
    try:
        count = db.session.query(String).count()

        if count == 0:
            return Response(
                response=json.dumps({"message": "No strings found"}),
                status=HTTPStatus.NOT_FOUND,
                mimetype="application/json",
            )

        # Get a random string
        random_offset = random.randint(0, count - 1)
        random_string = db.session.query(String).offset(random_offset).first()

        return Response(
            response=json.dumps({"random_string": random_string.value}),
            status=HTTPStatus.OK,
            mimetype="application/json",
        )

    except Exception as e:
        logger.error(f"Error getting random string: {e}")
        return Response(
            response=json.dumps({"error": str(e)}),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json",
        )
