# Source: src/core/services/jwt_service.py
import os
from datetime import datetime, timedelta, timezone

import jwt

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
JWT_ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("SECRET_KEY", "")
JWT_REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "")


class JWTService:
    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "access"})

        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"})

        return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str, verify_exp: bool = True) -> dict:
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
                options={"verify_exp": verify_exp},
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    @staticmethod
    def decode_refresh_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token, JWT_REFRESH_SECRET_KEY, algorithms=[JWT_ALGORITHM]
            )
            if payload.get("type") != "refresh":
                raise ValueError("Not a refresh token")
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid refresh token")
