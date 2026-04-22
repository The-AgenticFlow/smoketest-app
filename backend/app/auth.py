from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

security = HTTPBearer()
_security_dep = Depends(security)


def create_token(user_id: int, role: str = "user") -> str:
    expiry = datetime.utcnow() + timedelta(minutes=15)
    payload = {"sub": str(user_id), "role": role, "exp": expiry}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_token(
    credentials: HTTPAuthorizationCredentials = _security_dep,
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        ) from err
    except jwt.InvalidTokenError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from err


_verify_token_dep = Depends(verify_token)


def require_admin(
    payload: dict = _verify_token_dep,
) -> dict:
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin required"
        )
    return payload
