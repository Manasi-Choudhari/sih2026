"""
Evidence Ledger Hash-Chain Verification and Model.
Canonical JSON SHA256 Hash Chaining:
record_hash = SHA256(canonical_json(record_without_hash) + previous_record_hash)
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class EvidenceEntry(BaseModel):
    evidence_id: str
    case_id: str
    type: str
    source: str
    content: Dict[str, Any]
    content_hash: str
    prev_hash: str
    software_version: str = "VAJRA-1.0.0"
    timestamp: str

def compute_hash(record_data: Dict[str, Any], prev_hash: str) -> str:
    canonical = json.dumps(record_data, sort_keys=True, separators=(',', ':'))
    payload = canonical + prev_hash
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

class EvidenceLedger:
    def __init__(self):
        self._records: Dict[str, List[EvidenceEntry]] = {}
        self._seed_default_ledger()

    def _seed_default_ledger(self):
        now = datetime.now(timezone.utc).isoformat()
        
        # Build clean chain for case_s1
        entries = []
        prev = "GENESIS"
        
        c1 = {"tx_hash": "s1_tx1", "from": "s1_victim", "to": "s1_hop1", "amount": 2.5, "asset": "ETH"}
        h1 = compute_hash(c1, prev)
        entries.append(EvidenceEntry(
            evidence_id="ev_01", case_id="case_s1", type="TRANSACTION", source="ETH_CHAIN",
            content=c1, content_hash=h1, prev_hash=prev, timestamp=now
        ))
        
        c2 = {"tx_hash": "s1_tx2", "from": "s1_hop1", "to": "s1_vasp", "amount": 2.48, "asset": "ETH"}
        h2 = compute_hash(c2, h1)
        entries.append(EvidenceEntry(
            evidence_id="ev_02", case_id="case_s1", type="TRANSACTION", source="ETH_CHAIN",
            content=c2, content_hash=h2, prev_hash=h1, timestamp=now
        ))
        
        c3 = {"vasp": "DemoExchange", "address": "s1_vasp", "verified": True, "tier": "Strong"}
        h3 = compute_hash(c3, h2)
        entries.append(EvidenceEntry(
            evidence_id="ev_03", case_id="case_s1", type="ATTRIBUTION_LABEL", source="VASP_REGISTRY",
            content=c3, content_hash=h3, prev_hash=h2, timestamp=now
        ))
        
        self._records["case_s1"] = entries

    def get_entries(self, case_id: str) -> List[EvidenceEntry]:
        return self._records.get(case_id, [])

    def append_entry(self, case_id: str, entry_type: str, source: str, content: Dict[str, Any]) -> EvidenceEntry:
        entries = self._records.setdefault(case_id, [])
        prev = entries[-1].content_hash if entries else "GENESIS"
        c_hash = compute_hash(content, prev)
        record = EvidenceEntry(
            evidence_id=f"ev_{len(entries)+1:02d}",
            case_id=case_id,
            type=entry_type,
            source=source,
            content=content,
            content_hash=c_hash,
            prev_hash=prev,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        entries.append(record)
        return record

    def verify_chain(self, case_id: str) -> Dict[str, Any]:
        entries = self.get_entries(case_id)
        if not entries:
            return {"status": "PASS", "records_evaluated": 0, "is_tampered": False, "details": "Empty ledger (clean state)"}
            
        prev = "GENESIS"
        for idx, entry in enumerate(entries):
            expected = compute_hash(entry.content, prev)
            if expected != entry.content_hash:
                return {
                    "status": "FAIL",
                    "records_evaluated": idx + 1,
                    "is_tampered": True,
                    "details": f"Cryptographic tamper detected at record {entry.evidence_id}: expected {expected[:10]}..., got {entry.content_hash[:10]}..."
                }
            prev = entry.content_hash
            
        return {
            "status": "PASS",
            "records_evaluated": len(entries),
            "is_tampered": False,
            "details": f"Hash chain intact: all {len(entries)} evidence records cryptographically valid."
        }

evidence_ledger = EvidenceLedger()
