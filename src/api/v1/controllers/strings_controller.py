import logging
import random
from http import HTTPStatus

from flask import Blueprint, request
from pydantic import ValidationError

from src.api.v1.middlewares.auth_middleware import jwt_required
from src.core.metrics import STRINGS_RETRIEVED, STRINGS_SAVED
from src.core.models.string import String
from src.core.schemas.strings import (
    RandomStringResponseSchema,
    StringCreateResponseSchema,
    StringCreateSchema,
)
from src.factory import db, limiter
from src.utils import create_error_response, create_success_response

strings = Blueprint("strings", __name__)
logger = logging.getLogger(__name__)


@strings.route("/save", methods=["POST"])
@jwt_required
@limiter.limit("100 per minute")
def save_string():
    try:
        # Validate request format
        if not request.is_json:
            return create_error_response("Request must be JSON", HTTPStatus.BAD_REQUEST)

        # Validate string data with Pydantic
        try:
            string_data = StringCreateSchema(**request.json)
        except ValidationError as e:
            logger.info(f"Validation error: {e}")
            return create_error_response(
                f"Validation error: {e}", HTTPStatus.BAD_REQUEST
            )

        # Create and save the string
        new_string = String(value=string_data.string)
        db.session.add(new_string)
        db.session.commit()

        # Create response using Pydantic schema
        response_data = StringCreateResponseSchema(
            message="String saved successfully",
            status="success",
            id=new_string.id,
        )

        STRINGS_SAVED.inc()

        return create_success_response(response_data.model_dump(), HTTPStatus.CREATED)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving string: {e}")
        return create_error_response(
            "Internal server error", HTTPStatus.INTERNAL_SERVER_ERROR
        )


@strings.route("/random", methods=["GET"])
@limiter.limit("100 per minute")
def get_random_string():
    try:
        count = db.session.query(String).count()

        if count == 0:
            return create_error_response("No strings found", HTTPStatus.NOT_FOUND)

        random_offset = random.randint(0, count - 1)
        random_string = db.session.query(String).offset(random_offset).first()

        response_data = RandomStringResponseSchema(random_string=random_string.value)

        STRINGS_RETRIEVED.inc()

        return create_success_response(response_data.model_dump(), HTTPStatus.OK)

    except Exception as e:
        logger.error(f"Error getting random string: {e}")
        return create_error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
