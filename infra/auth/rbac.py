"""
Role-Based Access Control (RBAC) Module (T6)
Defines roles, permissions, role hierarchy, and route protection guards.
"""

from enum import Enum
from typing import List, Set, Dict, Optional, Callable, Any
from dataclasses import dataclass
import hashlib


# ---------------------------------------------------------------------------
# Inlined from jwt.py to keep rbac.py standalone (no __init__.py required).
# T1's FastAPI backend imports jwt.py and rbac.py independently.
# ---------------------------------------------------------------------------
class JWTError(Exception):
    """Raised when token validation or decoding fails."""
    pass


@dataclass
class TokenData:
    user_id: str
    username: str
    role: str
    exp: int
    iat: int
    extra: Dict[str, Any]


class Role(str, Enum):
    INVESTIGATOR = "investigator"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class Permission(str, Enum):
    # Case Management
    CASE_READ = "case:read"
    CASE_CREATE = "case:create"
    CASE_ASSIGN = "case:assign"

    # Tracing & Graph
    TRACE_EXECUTE = "trace:execute"
    GRAPH_READ = "graph:read"

    # Attribution & ATLAS
    ATTRIBUTION_READ = "attribution:read"
    ATLAS_READ = "atlas:read"

    # Evidence Ledger & Verification
    EVIDENCE_READ = "evidence:read"
    EVIDENCE_VERIFY = "evidence:verify"

    # Recommendations & Actions
    RECOMMENDATION_READ = "recommendation:read"
    RECOMMENDATION_CREATE = "recommendation:create"
    RECOMMENDATION_APPROVE = "recommendation:approve"  # SUPERVISOR ONLY

    # Reports & External
    REPORT_PREVIEW = "report:preview"
    REPORT_GENERATE = "report:generate"  # SUPERVISOR ONLY
    EXTERNAL_CALLBACK = "external:callback"

    # System & Audit
    AUDIT_READ = "audit:read"
    SYSTEM_RESET = "system:reset"
    USER_MANAGE = "user:manage"


# Permission Mappings
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.INVESTIGATOR: {
        Permission.CASE_READ,
        Permission.CASE_CREATE,
        Permission.TRACE_EXECUTE,
        Permission.GRAPH_READ,
        Permission.ATTRIBUTION_READ,
        Permission.ATLAS_READ,
        Permission.EVIDENCE_READ,
        Permission.RECOMMENDATION_READ,
        Permission.RECOMMENDATION_CREATE,
        Permission.REPORT_PREVIEW,
    },
    Role.SUPERVISOR: {
        # Inherits all Investigator permissions
        Permission.CASE_READ,
        Permission.CASE_CREATE,
        Permission.CASE_ASSIGN,
        Permission.TRACE_EXECUTE,
        Permission.GRAPH_READ,
        Permission.ATTRIBUTION_READ,
        Permission.ATLAS_READ,
        Permission.EVIDENCE_READ,
        Permission.EVIDENCE_VERIFY,
        Permission.RECOMMENDATION_READ,
        Permission.RECOMMENDATION_CREATE,
        Permission.RECOMMENDATION_APPROVE,  # Gatekeeper for VASP action
        Permission.REPORT_PREVIEW,
        Permission.REPORT_GENERATE,
        Permission.AUDIT_READ,
    },
    Role.ADMIN: {
        # All permissions
        *Permission,
    },
}


@dataclass
class User:
    user_id: str
    username: str
    role: Role
    full_name: str
    is_active: bool = True


class UnauthorizedRoleError(JWTError):
    """Raised when an authenticated user does not have the required role."""
    pass


class ForbiddenPermissionError(JWTError):
    """Raised when an authenticated user lacks the required permission."""
    pass


def has_permission(role: str | Role, permission: Permission) -> bool:
    """Checks if a given role possesses a specific permission."""
    try:
        role_enum = Role(role) if isinstance(role, str) else role
    except ValueError:
        return False
    return permission in ROLE_PERMISSIONS.get(role_enum, set())


def require_role(*allowed_roles: Role | str):
    """
    FastAPI dependency factory to enforce that the authenticated user has
    at least one of the specified roles.

    Usage:
        @app.post("/cases/{id}/recommendations/approve")
        def approve_recommendation(user: TokenData = Depends(require_role(Role.SUPERVISOR))):
            ...
    """
    valid_roles = {r.value if isinstance(r, Role) else str(r) for r in allowed_roles}

    def role_checker(user: TokenData) -> TokenData:
        if user.role not in valid_roles:
            raise UnauthorizedRoleError(
                f"Access denied. User '{user.username}' with role '{user.role}' "
                f"does not have permission. Required role(s): {list(valid_roles)}"
            )
        return user

    return role_checker


def require_permission(required_perm: Permission):
    """
    FastAPI dependency factory to enforce that the user possesses a specific permission.
    """
    def permission_checker(user: TokenData) -> TokenData:
        if not has_permission(user.role, required_perm):
            raise ForbiddenPermissionError(
                f"Action forbidden. User '{user.username}' lacks permission '{required_perm.value}'"
            )
        return user

    return permission_checker


# ==============================================================================
# Seeded Demo Users for Day 1-10 Development & Judging
# ==============================================================================
def _hash_pass(password: str) -> str:
    return hashlib.sha256(f"vajra_salt_{password}".encode('utf-8')).hexdigest()


DEMO_USERS = {
    "inv_sharma": {
        "user_id": "usr_01",
        "username": "inv_sharma",
        "password_hash": _hash_pass("investigator123"),
        "role": Role.INVESTIGATOR,
        "full_name": "Inspector R. Sharma",
    },
    "sup_verma": {
        "user_id": "usr_02",
        "username": "sup_verma",
        "password_hash": _hash_pass("supervisor123"),
        "role": Role.SUPERVISOR,
        "full_name": "Superintendent A. Verma",
    },
    "admin_vajra": {
        "user_id": "usr_03",
        "username": "admin_vajra",
        "password_hash": _hash_pass("admin123"),
        "role": Role.ADMIN,
        "full_name": "System Administrator",
    }
}


def authenticate_demo_user(username: str, password: str) -> Optional[Dict]:
    """Authenticates credentials against the built-in development users."""
    user = DEMO_USERS.get(username)
    if not user:
        return None
    if user["password_hash"] == _hash_pass(password):
        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"].value,
            "full_name": user["full_name"]
        }
    return None
