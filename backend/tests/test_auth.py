import jwt
import pytest

from app.auth import create_token, verify_token
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
    """BUG: create_token doesn't include 'role' in payload,
    so require_admin always rejects. This test documents the bug."""
    token = create_token(user_id=1)
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert "role" not in payload


def test_invalid_token_rejected():
    with pytest.raises(Exception):
        jwt.decode("invalid.token.here", settings.secret_key, algorithms=[settings.algorithm])
