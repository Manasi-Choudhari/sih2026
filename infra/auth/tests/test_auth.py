"""
Unit Tests for Auth & RBAC (T6 Task 2)
Compatible with both unittest and pytest.
"""

import unittest
from infra.auth.jwt import (
    create_access_token,
    decode_access_token,
    TokenExpiredError,
    InvalidTokenSignatureError,
    JWTError,
)
from infra.auth.rbac import (
    Role,
    Permission,
    has_permission,
    require_role,
    require_permission,
    UnauthorizedRoleError,
    ForbiddenPermissionError,
    authenticate_demo_user,
)


class TestAuthAndRBAC(unittest.TestCase):

    def test_token_creation_and_decode(self):
        payload = {
            "sub": "usr_01",
            "username": "inv_sharma",
            "role": Role.INVESTIGATOR.value,
            "org": "CyberCrimeUnit"
        }
        token = create_access_token(payload, expires_minutes=15)
        self.assertIsInstance(token, str)
        self.assertEqual(len(token.split('.')), 3)

        decoded = decode_access_token(token)
        self.assertEqual(decoded.user_id, "usr_01")
        self.assertEqual(decoded.username, "inv_sharma")
        self.assertEqual(decoded.role, "investigator")
        self.assertEqual(decoded.extra.get("org"), "CyberCrimeUnit")

    def test_expired_token_rejection(self):
        token = create_access_token({"sub": "usr_01", "role": "investigator"}, expires_minutes=-1)
        with self.assertRaises(TokenExpiredError):
            decode_access_token(token)

    def test_tampered_signature_rejection(self):
        token = create_access_token({"sub": "usr_01", "role": "investigator"})
        parts = token.split('.')
        tampered_payload = parts[1][:-2] + "AA"
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

        with self.assertRaises(JWTError):
            decode_access_token(tampered_token)

    def test_invalid_secret_key_rejection(self):
        token = create_access_token({"sub": "usr_01", "role": "investigator"}, secret_key="secret_a")
        with self.assertRaises(InvalidTokenSignatureError):
            decode_access_token(token, secret_key="secret_b")

    def test_role_hierarchy_and_permissions(self):
        self.assertTrue(has_permission(Role.INVESTIGATOR, Permission.CASE_READ))
        self.assertFalse(has_permission(Role.INVESTIGATOR, Permission.RECOMMENDATION_APPROVE))

        self.assertTrue(has_permission(Role.SUPERVISOR, Permission.CASE_READ))
        self.assertTrue(has_permission(Role.SUPERVISOR, Permission.RECOMMENDATION_APPROVE))
        self.assertTrue(has_permission(Role.SUPERVISOR, Permission.REPORT_GENERATE))

        self.assertTrue(has_permission(Role.ADMIN, Permission.SYSTEM_RESET))

    def test_require_role_guard(self):
        investigator_token = decode_access_token(
            create_access_token({"sub": "usr_01", "username": "inv", "role": Role.INVESTIGATOR.value})
        )
        supervisor_token = decode_access_token(
            create_access_token({"sub": "usr_02", "username": "sup", "role": Role.SUPERVISOR.value})
        )

        # Investigator check
        investigator_guard = require_role(Role.INVESTIGATOR, Role.SUPERVISOR)
        self.assertEqual(investigator_guard(investigator_token).username, "inv")

        # Supervisor-only check
        supervisor_guard = require_role(Role.SUPERVISOR)
        self.assertEqual(supervisor_guard(supervisor_token).username, "sup")

        with self.assertRaises(UnauthorizedRoleError):
            supervisor_guard(investigator_token)

    def test_demo_user_authentication(self):
        # Correct credentials
        user = authenticate_demo_user("inv_sharma", "investigator123")
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "investigator")

        # Wrong password
        self.assertIsNone(authenticate_demo_user("inv_sharma", "wrongpassword"))

        # Unknown user
        self.assertIsNone(authenticate_demo_user("unknown_officer", "password"))


if __name__ == "__main__":
    unittest.main()
