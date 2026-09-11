"""
Unit Tests for Audit Logging and Rate Limiting Middleware (T6 Task 4 & 5)
Compatible with unittest and pytest.
"""

import unittest
import time
from infra.rate_limiting.middleware import (
    RateLimiter,
    RateLimitExceededError,
    ExplorerCircuitBreaker,
    CircuitBreakerOpenError,
)
from infra.audit.audit_middleware import (
    AuditEventStore,
    AuditLogger,
    AuditAction,
)


class TestRateLimitingAndAudit(unittest.TestCase):

    def setUp(self):
        self.audit_store = AuditEventStore()

    def test_rate_limiter_permits_within_limit(self):
        limiter = RateLimiter(default_limit=3, default_window=10)
        client_key = "192.168.1.100"

        # 3 calls should pass
        allowed1, remaining1, _ = limiter.is_allowed(client_key)
        allowed2, remaining2, _ = limiter.is_allowed(client_key)
        allowed3, remaining3, _ = limiter.is_allowed(client_key)

        self.assertTrue(allowed1)
        self.assertEqual(remaining1, 2)
        self.assertTrue(allowed2)
        self.assertEqual(remaining2, 1)
        self.assertTrue(allowed3)
        self.assertEqual(remaining3, 0)

        # 4th call should fail
        allowed4, remaining4, retry_after = limiter.is_allowed(client_key)
        self.assertFalse(allowed4)
        self.assertEqual(remaining4, 0)
        self.assertGreater(retry_after, 0)

        # check() should raise RateLimitExceededError
        with self.assertRaises(RateLimitExceededError):
            limiter.check(client_key)

    def test_circuit_breaker_degraded_mode(self):
        cb = ExplorerCircuitBreaker(failure_threshold=2, recovery_timeout=5)
        service = "etherscan_api"

        # Record cached data
        cb.record_success(service, cache_key="addr_0x123", data={"balance": "10.5 ETH"})

        self.assertTrue(cb.can_execute(service))
        self.assertFalse(cb.is_degraded(service))

        # 1st failure - circuit still closed
        cb.record_failure(service)
        self.assertTrue(cb.can_execute(service))

        # 2nd failure - circuit trips open!
        tripped = cb.record_failure(service)
        self.assertTrue(tripped)
        self.assertTrue(cb.is_degraded(service))
        self.assertFalse(cb.can_execute(service))

        # Fallback returns cached data without crashing
        cached_data, is_degraded = cb.get_fallback_or_raise(service, cache_key="addr_0x123")
        self.assertEqual(cached_data["balance"], "10.5 ETH")
        self.assertTrue(is_degraded)

        # Uncached key raises CircuitBreakerOpenError
        with self.assertRaises(CircuitBreakerOpenError):
            cb.get_fallback_or_raise(service, cache_key="uncached_address")

    def test_audit_event_capture_and_case_filtering(self):
        case_id = "case_2026_001"
        actor_id = "inv_sharma"

        # 1. Create case
        evt1 = self.audit_store.record_event(
            actor_id=actor_id,
            action=AuditAction.CASE_CREATED,
            target_id=case_id,
            case_id=case_id,
            details={"victim_wallet": "0xVictim123"}
        )
        self.assertEqual(evt1.action, "case_created")
        self.assertEqual(evt1.case_id, case_id)

        # 2. Start trace
        evt2 = self.audit_store.record_event(
            actor_id=actor_id,
            action=AuditAction.TRACE_STARTED,
            target_id="trace_session_01",
            case_id=case_id,
            details={"max_depth": 8}
        )

        # 3. Another case event
        self.audit_store.record_event(
            actor_id="other_actor",
            action=AuditAction.CASE_CREATED,
            target_id="case_other",
            case_id="case_other"
        )

        # Retrieve events for case_2026_001
        case_events = self.audit_store.get_events_for_case(case_id)
        self.assertEqual(len(case_events), 2)
        self.assertEqual(case_events[0]["action"], "case_created")
        self.assertEqual(case_events[1]["action"], "trace_started")

    def test_audit_logger_facade(self):
        event = AuditLogger.log(
            actor_id="sup_verma",
            action=AuditAction.RECOMMENDATION_APPROVED,
            target_id="rec_99",
            case_id="case_2026_002",
            details={"action": "FREEZE_REQUEST_VASP"}
        )
        self.assertEqual(event.actor_id, "sup_verma")
        self.assertEqual(event.action, "recommendation_approved")


if __name__ == "__main__":
    unittest.main()
