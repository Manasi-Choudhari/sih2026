"""
Ethereum explorer adapter for VAJRA.
Interacts with Etherscan-compatible APIs to fetch normal transactions,
with retries, rate limiting, and cached fallback support.
"""

from __future__ import annotations
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv
load_dotenv()

from blockchain.adapters.base import BaseAdapter
from blockchain.normalization.normalize import NormalizedTransaction


class EtherscanAdapter(BaseAdapter):
    """Adapter for fetching Ethereum transactions via Etherscan API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.etherscan.io/v2/api",
        timeout_seconds: int = 10,
        max_retries: int = 3,
    ):
        super().__init__(api_key=api_key or os.getenv("EXPLORER_API_KEY_ETH", ""), timeout_seconds=timeout_seconds, max_retries=max_retries)
        self.base_url = base_url
        self._cache: Dict[str, List[NormalizedTransaction]] = {}

    def get_address_transactions(
        self,
        address: str,
        limit: int = 50,
        page: int = 1,
    ) -> List[NormalizedTransaction]:
        """Fetch regular transactions for an Ethereum address."""
        cache_key = f"{address.lower()}:{page}:{limit}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self.api_key:
            # Fallback to local cached fixture if no key provided
            return self._cache.get(cache_key, [])

        params = {
            "chainid": 1,
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": page,
            "offset": limit,
            "sort": "desc",
            "apikey": self.api_key,
        }

        retries = 0
        backoff = 1.0
        while retries < self.max_retries:
            try:
                response = requests.get(self.base_url, params=params, timeout=self.timeout_seconds)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    result = data.get("result", [])
                    if status == "1" and isinstance(result, list):
                        parsed = [self._parse_tx(tx, address) for tx in result if tx.get("isError") == "0"]
                        self._cache[cache_key] = parsed
                        return parsed
                    elif status == "0" and data.get("message") == "No transactions found":
                        return []
                    else:
                        time.sleep(backoff)
                        backoff *= 2
                        retries += 1
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
        """Fetch single transaction by hash via Etherscan proxy."""
        if not self.api_key:
            return None

        params = {
            "module": "proxy",
            "action": "eth_getTransactionByHash",
            "txhash": tx_hash,
            "apikey": self.api_key,
        }

        try:
            resp = requests.get(self.base_url, params=params, timeout=self.timeout_seconds)
            if resp.status_code == 200:
                data = resp.json()
                raw_tx = data.get("result")
                if raw_tx and isinstance(raw_tx, dict):
                    val_wei = int(raw_tx.get("value", "0x0"), 16)
                    val_eth = val_wei / 1e18
                    return NormalizedTransaction(
                        tx_hash=raw_tx.get("hash", tx_hash),
                        chain="ETH",
                        from_address=raw_tx.get("from", "").lower(),
                        to_address=(raw_tx.get("to") or "").lower(),
                        block_height=int(raw_tx.get("blockNumber", "0x0"), 16),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        amount=val_eth,
                        asset="ETH",
                        direction="out",
                        is_bridge_leg=False,
                        confidence_of_link=1.0,
                    )
        except Exception:
            pass
        return None

    def _parse_tx(self, raw_tx: dict, query_address: str) -> NormalizedTransaction:
        """Parse raw Etherscan tx into NormalizedTransaction."""
        from_addr = (raw_tx.get("from") or "").lower()
        to_addr = (raw_tx.get("to") or "").lower()
        query_addr_lower = query_address.lower()
        direction = "out" if from_addr == query_addr_lower else "in"
        
        val_wei = int(raw_tx.get("value", 0))
        val_eth = val_wei / 1e18
        
        ts_int = int(raw_tx.get("timeStamp", int(time.time())))
        dt = datetime.fromtimestamp(ts_int, timezone.utc)

        return NormalizedTransaction(
            tx_hash=raw_tx.get("hash", ""),
            chain="ETH",
            from_address=from_addr,
            to_address=to_addr,
            block_height=int(raw_tx.get("blockNumber", 0)),
            timestamp=dt.isoformat(),
            amount=val_eth,
            asset="ETH",
            direction=direction,
            is_bridge_leg=False,
            confidence_of_link=1.0,
        )

    def inject_mock_transactions(self, address: str, txs: List[NormalizedTransaction]) -> None:
        """Inject transactions for mock/fixture testing."""
        cache_key = f"{address.lower()}:1:50"
        self._cache[cache_key] = txs
