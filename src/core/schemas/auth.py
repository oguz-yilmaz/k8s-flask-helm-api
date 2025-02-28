from typing import Optional

from pydantic import BaseModel, EmailStr, Field, SecretStr

from src.core.schemas.base import BaseSchema, SuccessResponseSchema


class LoginRequestSchema(BaseSchema):
    """Schema for login request validation"""

    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequestSchema(BaseSchema):
    """Schema for registration request validation"""

    email: EmailStr
    password: str = Field(min_length=8)


class RefreshTokenRequestSchema(BaseSchema):
    """Schema for token refresh request validation"""

    refresh_token: str


class TokenResponseSchema(SuccessResponseSchema):
    """Schema for token response"""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class UserSchema(BaseSchema):
    """Schema for user data"""

    id: str
    email: EmailStr


class TokenPayloadSchema(BaseSchema):
    """Schema for JWT token payload"""

    user_id: str
    email: EmailStr
    exp: Optional[int] = None
    iat: Optional[int] = None
    type: Optional[str] = None
