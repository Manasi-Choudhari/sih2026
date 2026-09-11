"""
Audit Logging Middleware (T6 Task 5)
Captures ordered audit event trails for state-changing operations and security events.
Matches the PostgreSQL AuditEvent contract specified in BUILD.md.
"""

import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


class AuditAction(str, Enum):
    CASE_CREATED = "case_created"
    CASE_ASSIGNED = "case_assigned"
    TRACE_STARTED = "trace_started"
    TRACE_TERMINATED = "trace_terminated"
    ATTRIBUTION_CALCULATED = "attribution_calculated"
    RECOMMENDATION_CREATED = "recommendation_created"
    RECOMMENDATION_APPROVED = "recommendation_approved"
    RECOMMENDATION_REJECTED = "recommendation_rejected"
    REPORT_GENERATED = "report_generated"
    EVIDENCE_VERIFIED = "evidence_verified"
    EVIDENCE_TAMPER_DETECTED = "evidence_tamper_detected"
    UNAUTHORIZED_ACCESS_ATTEMPT = "unauthorized_access_attempt"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


@dataclass
class AuditEvent:
    event_id: str
    actor_id: str
    action: str
    target_id: str
    timestamp: str  # ISO 8601 UTC
    case_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditEventStore:
    """
    In-memory audit trail store with ordered retrieval.
    Can sync to PostgreSQL 'audit_event' table when database connection is live.
    """
    def __init__(self):
        self._events: List[AuditEvent] = []

    def record_event(
        self,
        actor_id: str,
        action: AuditAction | str,
        target_id: str,
        case_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Records an immutable audit event."""
        action_str = action.value if isinstance(action, AuditAction) else str(action)
        event = AuditEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            actor_id=actor_id,
            action=action_str,
            target_id=target_id,
            case_id=case_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=details or {},
            ip_address=ip_address
        )
        self._events.append(event)
        return event

    def get_events_for_case(self, case_id: str) -> List[Dict[str, Any]]:
        """Returns all events matching case_id ordered chronologically."""
        matching = [e for e in self._events if e.case_id == case_id or e.target_id == case_id]
        matching.sort(key=lambda x: x.timestamp)
        return [e.to_dict() for e in matching]

    def get_events_for_actor(self, actor_id: str) -> List[Dict[str, Any]]:
        matching = [e for e in self._events if e.actor_id == actor_id]
        matching.sort(key=lambda x: x.timestamp)
        return [e.to_dict() for e in matching]

    def get_all_events(self) -> List[Dict[str, Any]]:
        sorted_events = sorted(self._events, key=lambda x: x.timestamp)
        return [e.to_dict() for e in sorted_events]

    def clear(self):
        """Used by test resets."""
        self._events.clear()


# Global audit singleton
audit_event_store = AuditEventStore()


class AuditLogger:
    """Convenience logger facade for route handlers and background jobs."""
    @staticmethod
    def log(
        actor_id: str,
        action: AuditAction | str,
        target_id: str,
        case_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditEvent:
        return audit_event_store.record_event(
            actor_id=actor_id,
            action=action,
            target_id=target_id,
            case_id=case_id,
            details=details,
            ip_address=ip_address
        )
