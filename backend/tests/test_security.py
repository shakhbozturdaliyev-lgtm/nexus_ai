"""Unit tests for cryptographic security and token management."""

from datetime import timedelta
from backend.app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    """Verify password hash generation and verification."""
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_lifecycle():
    """Verify JWT access token creation and decoding."""
    subject = "admin@demoelectronics.uz"
    claims = {"role": "owner", "business_id": 1}

    token = create_access_token(subject=subject, claims=claims)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == subject
    assert payload["role"] == "owner"
    assert payload["business_id"] == 1


def test_expired_jwt():
    """Verify expired token rejection."""
    subject = "user@test.uz"
    token = create_access_token(
        subject=subject, expires_delta=timedelta(seconds=-10)
    )
    payload = decode_access_token(token)
    assert payload is None
