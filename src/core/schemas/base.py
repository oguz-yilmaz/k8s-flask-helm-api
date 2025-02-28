from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base Pydantic model with common configuration"""

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )


class ErrorResponseSchema(BaseSchema):
    """Schema for error responses"""

    status: str = "error"
    message: str
    error_code: Optional[str] = None


class SuccessResponseSchema(BaseSchema):
    """Schema for success responses"""

    status: str = "success"
    message: str


T = TypeVar("T")


class PaginatedResponseSchema(BaseSchema, Generic[T]):
    """Schema for paginated results"""

    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
