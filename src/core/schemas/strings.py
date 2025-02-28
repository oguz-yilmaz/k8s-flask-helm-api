from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator

from src.core.schemas.base import BaseSchema, SuccessResponseSchema


class StringSchema(BaseSchema):
    """Schema for string model"""

    id: int
    value: str
    created_at: Optional[datetime] = None


class StringCreateSchema(BaseSchema):
    """Schema for string creation validation"""

    string: str = Field(min_length=1, max_length=10000)

    @field_validator("string")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("String cannot be empty or just whitespace")
        return v


class StringCreateResponseSchema(SuccessResponseSchema):
    """Schema for string creation response"""

    id: int


class RandomStringResponseSchema(BaseSchema):
    """Schema for random string response"""

    random_string: str
