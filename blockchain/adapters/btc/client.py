"""
Bitcoin explorer adapter for VAJRA.
Interacts with Blockchair or Mempool API to fetch UTXO transactions,
with retries, rate limiting, and cached fallback support.
"""

from __future__ import annotations
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
import requests

from blockchain.adapters.base import BaseAdapter
from blockchain.normalization.normalize import NormalizedTransaction


class BlockchairBtcAdapter(BaseAdapter):
    """Adapter for fetching Bitcoin transactions via Blockchair API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.blockchair.com/bitcoin",
        timeout_seconds: int = 10,
        max_retries: int = 3,
    ):
        super().__init__(api_key=api_key or os.getenv("EXPLORER_API_KEY_BTC", ""), timeout_seconds=timeout_seconds, max_retries=max_retries)
        self.base_url = base_url
        self._cache: Dict[str, List[NormalizedTransaction]] = {}

    def get_address_transactions(
        self,
        address: str,
        limit: int = 50,
        page: int = 1,
    ) -> List[NormalizedTransaction]:
        """Fetch transactions for a Bitcoin address."""
        cache_key = f"{address}:{page}:{limit}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self.api_key:
            # Fallback to local cached fixture if no key provided
            return self._cache.get(cache_key, [])

        url = f"{self.base_url}/dashboards/address/{address}"
        params = {
            "transaction_details": "true",
            "limit": limit,
            "offset": (page - 1) * limit,
        }
        if self.api_key:
            params["key"] = self.api_key

        retries = 0
        backoff = 1.0
        while retries < self.max_retries:
            try:
                response = requests.get(url, params=params, timeout=self.timeout_seconds)
                if response.status_code == 200:
                    data = response.json()
                    addr_data = data.get("data", {}).get(address, {})
                    tx_list = addr_data.get("transactions", [])
                    parsed = [self._parse_tx(tx, address) for tx in tx_list]
                    self._cache[cache_key] = parsed
                    return parsed
                elif response.status_code == 404:
                    return []
                else:
                    time.sleep(backoff)
                    backoff *= 2
                    retries += 1
            except Exception:
                time.sleep(backoff)
                backoff *= 2
                retries += 1

        return self._cache.get(cache_key, [])

    def get_transaction_by_hash(self, tx_hash: str) -> Optional[NormalizedTransaction]:
        """Fetch details for a specific Bitcoin transaction."""
        url = f"{self.base_url}/dashboards/transaction/{tx_hash}"
        params = {}
        if self.api_key:
            params["key"] = self.api_key

        try:
            resp = requests.get(url, params=params, timeout=self.timeout_seconds)
            if resp.status_code == 200:
                data = resp.json()
                tx_data = data.get("data", {}).get(tx_hash, {}).get("transaction", {})
                if tx_data:
                    return self._parse_tx(tx_data, "")
        except Exception:
            pass
        return None

    def _parse_tx(self, raw_tx: dict, query_address: str) -> NormalizedTransaction:
        """Parse raw Blockchair tx dictionary into NormalizedTransaction."""
        tx_hash = raw_tx.get("hash", "")
        block_id = int(raw_tx.get("block_id", 0))
        time_str = raw_tx.get("time", datetime.now(timezone.utc).isoformat())
        
        # Blockchair amounts are in satoshis (1 BTC = 100,000,000 satoshis)
        satoshis = raw_tx.get("balance_change", raw_tx.get("output_total", 0))
        amount_btc = abs(satoshis) / 1e8
        direction = "out" if satoshis < 0 else "in"

        return NormalizedTransaction(
            tx_hash=tx_hash,
            chain="BTC",
            from_address=query_address if direction == "out" else "btc_sender",
            to_address=query_address if direction == "in" else "btc_recipient",
            block_height=block_id,
            timestamp=time_str,
            amount=amount_btc,
            asset="BTC",
            direction=direction,
            is_bridge_leg=False,
            confidence_of_link=1.0,
        )

    def inject_mock_transactions(self, address: str, txs: List[NormalizedTransaction]) -> None:
        """Inject transactions for mock/fixture testing."""
        cache_key = f"{address}:1:50"
        self._cache[cache_key] = txs
