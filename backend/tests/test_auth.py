import jwt
import pytest

from app.auth import create_token
from app.config import settings


def test_create_token():
    token = create_token(user_id=1)
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "1"


def test_token_expiry():
    token = create_token(user_id=1)
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert "exp" in payload


def test_admin_check_missing_role():
    """Role should now be included in token payload with default value 'user'"""
    token = create_token(user_id=1)
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert "role" in payload
    assert payload["role"] == "user"


def test_admin_token_passes_require_admin():
    """Admin token should have role='admin' in payload"""
    token = create_token(user_id=1, role="admin")
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert "role" in payload
    assert payload["role"] == "admin"


def test_user_token_fails_require_admin():
    """User token should have role='user' in payload (not admin)"""
    token = create_token(user_id=1, role="user")
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert "role" in payload
    assert payload["role"] == "user"
    assert payload["role"] != "admin"


def test_invalid_token_rejected():
    with pytest.raises(jwt.InvalidTokenError):
        jwt.decode("invalid.token.here", settings.secret_key, algorithms=[settings.algorithm])
