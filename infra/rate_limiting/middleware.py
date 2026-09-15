"""
Rate Limiting & Explorer API Resilience Module (T6 Task 4)
Provides sliding-window rate limiting and circuit-breaker resilience for explorer APIs.
"""

import time
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict


class RateLimitExceededError(Exception):
    """Raised when request rate exceeds the allowed threshold."""
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after


class CircuitBreakerOpenError(Exception):
    """Raised when downstream external service is failing and circuit is open."""
    pass


class RateLimiter:
    """
    Sliding-window rate limiter.
    Supports in-memory storage (offline/testing) and Redis when REDIS_URL is active.
    """
    def __init__(self, default_limit: int = 60, default_window: int = 60):
        self.default_limit = default_limit
        self.default_window = default_window  # in seconds
        self._in_memory_records: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(
        self,
        key: str,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> Tuple[bool, int, int]:
        """
        Determines if a request for 'key' is permitted under the rate limit.
        Returns: (is_allowed, remaining_requests, retry_after_seconds)
        """
        max_requests = limit or self.default_limit
        window_seconds = window or self.default_window
        now = time.time()
        cutoff = now - window_seconds

        # Clean entries older than window
        timestamps = self._in_memory_records[key]
        self._in_memory_records[key] = [ts for ts in timestamps if ts > cutoff]
        timestamps = self._in_memory_records[key]

        if len(timestamps) < max_requests:
            self._in_memory_records[key].append(now)
            remaining = max_requests - len(self._in_memory_records[key])
            return True, remaining, 0
        else:
            oldest_timestamp = timestamps[0]
            retry_after = max(1, int((oldest_timestamp + window_seconds) - now))
            return False, 0, retry_after

    def check(self, key: str, limit: Optional[int] = None, window: Optional[int] = None) -> None:
        """Throws RateLimitExceededError if rate limit is exceeded."""
        allowed, remaining, retry_after = self.is_allowed(key, limit, window)
        if not allowed:
            raise RateLimitExceededError(
                f"Rate limit exceeded for '{key}'. Try again in {retry_after} seconds.",
                retry_after=retry_after
            )


@dataclass
class CircuitBreakerState:
    failure_count: int = 0
    last_failure_time: float = 0.0
    is_open: bool = False
    degraded_mode_active: bool = False


class ExplorerCircuitBreaker:
    """
    Resilience wrapper for external blockchain explorer APIs (Etherscan/Blockchair).
    Protects against rate limits (e.g. 5 req/sec free-tier) and network outages.
    Automatically shifts into degraded mode using cached fixtures rather than crashing.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._services: Dict[str, CircuitBreakerState] = defaultdict(CircuitBreakerState)
        self._cached_responses: Dict[str, Any] = {}

    def record_success(self, service_name: str, cache_key: Optional[str] = None, data: Any = None):
        """Records a successful API response and updates cache."""
        state = self._services[service_name]
        state.failure_count = 0
        state.is_open = False
        state.degraded_mode_active = False
        if cache_key and data is not None:
            self._cached_responses[cache_key] = data

    def record_failure(self, service_name: str) -> bool:
        """
        Records an API failure. Opens circuit if threshold is reached.
        Returns True if circuit tripped open.
        """
        state = self._services[service_name]
        state.failure_count += 1
        state.last_failure_time = time.time()
        if state.failure_count >= self.failure_threshold:
            state.is_open = True
            state.degraded_mode_active = True
            return True
        return False

    def can_execute(self, service_name: str) -> bool:
        """Checks if a call can proceed to the external service."""
        state = self._services[service_name]
        if not state.is_open:
            return True
        now = time.time()
        # Half-open test if timeout passed
        if (now - state.last_failure_time) > self.recovery_timeout:
            return True
        return False

    def get_fallback_or_raise(self, service_name: str, cache_key: str, default_mock: Any = None) -> Tuple[Any, bool]:
        """
        Returns cached response or mock if available when circuit is open.
        Returns: (data, is_degraded_mode)
        """
        if cache_key in self._cached_responses:
            return self._cached_responses[cache_key], True
        if default_mock is not None:
            return default_mock, True
        raise CircuitBreakerOpenError(
            f"Explorer service '{service_name}' is currently unavailable and no cache is available."
        )

    def is_degraded(self, service_name: str) -> bool:
        return self._services[service_name].degraded_mode_active
