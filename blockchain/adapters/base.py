"""
Base blockchain explorer adapter interface.
Provides common interfaces for fetching, retrying, and parsing transactions
from live APIs or synthetic local fixtures.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from blockchain.normalization.normalize import NormalizedTransaction


class BaseAdapter(ABC):
    """Abstract base adapter for blockchain data retrieval."""

    def __init__(self, api_key: Optional[str] = None, timeout_seconds: int = 10, max_retries: int = 3):
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @abstractmethod
    def get_address_transactions(
        self,
        address: str,
        limit: int = 50,
        page: int = 1,
    ) -> List[NormalizedTransaction]:
        """Fetch transactions for a given wallet address and return normalized transactions."""
        pass

    @abstractmethod
    def get_transaction_by_hash(self, tx_hash: str) -> Optional[NormalizedTransaction]:
        """Fetch transaction details for a specific hash."""
        pass
