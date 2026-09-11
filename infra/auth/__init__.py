"""
VAJRA Security & Authentication Package (T6)
Provides JWT signing, token decoding, and Role-Based Access Control (RBAC).
"""

from .jwt import (
    create_access_token,
    decode_access_token,
    get_current_user,
    TokenData,
    JWTError,
)
from .rbac import (
    Role,
    User,
    has_permission,
    require_role,
    DEMO_USERS,
    authenticate_demo_user,
)

__all__ = [
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "TokenData",
    "JWTError",
    "Role",
    "User",
    "has_permission",
    "require_role",
    "DEMO_USERS",
    "authenticate_demo_user",
]
