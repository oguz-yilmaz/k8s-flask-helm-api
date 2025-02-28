from http import HTTPStatus
from typing import Any, Dict

from flask import Response, json

from src.core.schemas.base import ErrorResponseSchema


def create_error_response(message: str, status_code: int) -> Response:
    """Create a standardized error response"""
    error_schema = ErrorResponseSchema(message=message, status="failed")
    return Response(
        response=json.dumps(error_schema.model_dump()),
        status=status_code,
        mimetype="application/json",
    )


def create_success_response(
    data: Dict[str, Any], status_code: int = HTTPStatus.OK
) -> Response:
    """Create a standardized success response"""
    return Response(
        response=json.dumps(data),
        status=status_code,
        mimetype="application/json",
    )
