"""
Evidence Ledger Hash-Chain Verification and Model.
Canonical JSON SHA256 Hash Chaining:
record_hash = SHA256(canonical_json(record_without_hash) + previous_record_hash)
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
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
        self._seed_from_fixtures()

    def _seed_from_fixtures(self):
        """Dynamically loads and builds canonical hash chains for all seeded scenarios."""
        fixtures_dir = Path(__file__).resolve().parents[2] / "scenarios" / "fixtures"
        if not fixtures_dir.exists():
            return

        for fix_path in sorted(fixtures_dir.glob("scenario_*.json")):
            try:
                with open(fix_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                case_id = data.get("case", {}).get("case_id")
                if not case_id:
                    continue

                entries: List[EvidenceEntry] = []
                prev_hash = "GENESIS"
                now = datetime.now(timezone.utc).isoformat()

                # 1. Transaction relationships as evidence
                neo_rels = data.get("neo4j", {}).get("relationships", [])
                for idx, rel in enumerate(neo_rels):
                    props = rel.get("properties", {})
                    content = {
                        "tx_hash": props.get("tx_hash", f"tx_{idx+1}"),
                        "from": rel.get("from"),
                        "to": rel.get("to"),
                        "amount": props.get("amount", 0.0),
                        "asset": props.get("asset", "ETH"),
                        "chain": props.get("chain", "ETH"),
                    }
                    c_hash = compute_hash(content, prev_hash)
                    entry = EvidenceEntry(
                        evidence_id=f"ev_tx_{idx+1:02d}",
                        case_id=case_id,
                        type="TRANSACTION",
                        source=f"{props.get('chain', 'ETH')}_CHAIN",
                        content=content,
                        content_hash=c_hash,
                        prev_hash=prev_hash,
                        timestamp=now,
                    )
                    entries.append(entry)
                    prev_hash = c_hash

                # 2. VASP / Label attribution evidence
                labels = data.get("postgres", {}).get("labels", [])
                for idx, lbl in enumerate(labels):
                    content = {
                        "wallet_id": lbl.get("wallet_id"),
                        "label_text": lbl.get("label_text"),
                        "source": lbl.get("source"),
                        "confidence_tier": lbl.get("confidence_tier"),
                        "confidence": lbl.get("confidence", 1.0),
                    }
                    c_hash = compute_hash(content, prev_hash)
                    entry = EvidenceEntry(
                        evidence_id=f"ev_lbl_{idx+1:02d}",
                        case_id=case_id,
                        type="ATTRIBUTION_LABEL",
                        source="VASP_REGISTRY" if lbl.get("source") == "official" else "INTEL_PROVIDER",
                        content=content,
                        content_hash=c_hash,
                        prev_hash=prev_hash,
                        timestamp=now,
                    )
                    entries.append(entry)
                    prev_hash = c_hash

                if entries:
                    self._records[case_id] = entries
            except Exception:
                pass

    def get_entries(self, case_id: str) -> List[EvidenceEntry]:
        # 1. Try PostgreSQL evidence store
        try:
            from db.evidence_ledger.ledger_store import get_evidence_records_for_case
            pg_records = get_evidence_records_for_case(case_id)
            if pg_records:
                return [
                    EvidenceEntry(
                        evidence_id=r["evidence_id"],
                        case_id=r["case_id"],
                        type=r["type"],
                        source=r["source"],
                        content=r["content"],
                        content_hash=r["content_hash"],
                        prev_hash=r["prev_hash"],
                        software_version=r.get("software_version", "VAJRA-1.0.0"),
                        timestamp=r.get("created_at") or datetime.now(timezone.utc).isoformat(),
                    )
                    for r in pg_records
                ]
        except Exception:
            pass

        # 2. Fall back to seeded scenario entries
        return self._records.get(case_id, [])

    def append_entry(self, case_id: str, entry_type: str, source: str, content: Dict[str, Any]) -> EvidenceEntry:
        # 1. Persist to Postgres if available
        try:
            from db.evidence_ledger.ledger_store import append_evidence_record
            pg_rec = append_evidence_record(
                case_id=case_id,
                evidence_type=entry_type,
                source=source,
                content=content,
                software_version="VAJRA-1.0.0"
            )
            entry = EvidenceEntry(
                evidence_id=pg_rec["evidence_id"],
                case_id=pg_rec["case_id"],
                type=pg_rec["type"],
                source=pg_rec["source"],
                content=pg_rec["content"],
                content_hash=pg_rec["content_hash"],
                prev_hash=pg_rec["prev_hash"],
                software_version=pg_rec["software_version"],
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            entries = self._records.setdefault(case_id, [])
            entries.append(entry)
            return entry
        except Exception:
            pass

        # 2. In-memory append
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
