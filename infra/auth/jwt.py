"""
JWT Token Generation and Verification Module (T6)
Compliant with RFC 7519 JSON Web Token standard.
Uses standard HMAC-SHA256 (HS256) signing.
"""

import os
import json
import base64
import hmac
import hashlib
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Configuration from environment
JWT_SECRET = os.getenv("JWT_SECRET", "vajra_jwt_super_secret_signing_key_change_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))


class JWTError(Exception):
    """Raised when token validation or decoding fails."""
    pass


class TokenExpiredError(JWTError):
    """Raised when token has passed its expiration time."""
    pass


class InvalidTokenSignatureError(JWTError):
    """Raised when token signature does not match."""
    pass


@dataclass
class TokenData:
    user_id: str
    username: str
    role: str
    exp: int
    iat: int
    extra: Dict[str, Any]


def _base64url_encode(data: bytes) -> str:
    """Encodes bytes to URL-safe base64 string without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64url_decode(data: str) -> bytes:
    """Decodes URL-safe base64 string with restored padding."""
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data.encode('utf-8'))


def create_access_token(
    data: Dict[str, Any],
    expires_minutes: Optional[int] = None,
    secret_key: Optional[str] = None
) -> str:
    """
    Creates an RFC 7519 compliant HS256 JWT access token.
    """
    secret = secret_key or JWT_SECRET
    current_time = int(time.time())
    ttl_seconds = (expires_minutes if expires_minutes is not None else ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    expire_time = current_time + ttl_seconds

    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = dict(data)
    payload.setdefault("iat", current_time)
    payload["exp"] = expire_time

    header_bytes = json.dumps(header, separators=(',', ':'), sort_keys=True).encode('utf-8')
    payload_bytes = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')

    encoded_header = _base64url_encode(header_bytes)
    encoded_payload = _base64url_encode(payload_bytes)

    signing_input = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    signature = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    encoded_signature = _base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def decode_access_token(token: str, secret_key: Optional[str] = None) -> TokenData:
    """
    Decodes and cryptographically verifies an HS256 JWT token.
    Raises TokenExpiredError or InvalidTokenSignatureError on failure.
    """
    secret = secret_key or JWT_SECRET
    parts = token.strip().split('.')
    if len(parts) != 3:
        raise JWTError("Invalid JWT structure: token must have exactly 3 parts separated by dots")

    encoded_header, encoded_payload, encoded_signature = parts

    # 1. Verify signature
    signing_input = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    expected_signature = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    actual_signature = _base64url_decode(encoded_signature)

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise InvalidTokenSignatureError("Cryptographic signature verification failed")

    # 2. Decode payload
    try:
        payload_bytes = _base64url_decode(encoded_payload)
        payload = json.loads(payload_bytes.decode('utf-8'))
    except Exception as e:
        raise JWTError(f"Malformed token payload: {str(e)}")

    # 3. Check expiration
    current_time = int(time.time())
    exp = payload.get("exp")
    if exp is None:
        raise JWTError("Missing 'exp' claim in token")
    if current_time > exp:
        raise TokenExpiredError(f"Token expired at {exp}, current time is {current_time}")

    user_id = str(payload.get("sub", payload.get("user_id", "")))
    username = str(payload.get("username", user_id))
    role = str(payload.get("role", "investigator"))
    iat = int(payload.get("iat", current_time))

    extra = {k: v for k, v in payload.items() if k not in ("sub", "user_id", "username", "role", "exp", "iat")}

    return TokenData(
        user_id=user_id,
        username=username,
        role=role,
        exp=exp,
        iat=iat,
        extra=extra
    )


# ==============================================================================
# FastAPI Security Dependency Helper
# ==============================================================================
async def get_current_user(authorization: Optional[str] = None) -> TokenData:
    """
    FastAPI dependency to extract and validate the Bearer token from the
    Authorization header.
    Can be used with `Depends(get_current_user)` in route definitions.
    """
    if not authorization:
        raise JWTError("Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise JWTError("Invalid Authorization header format. Expected 'Bearer <token>'")

    token = parts[1]
    return decode_access_token(token)
