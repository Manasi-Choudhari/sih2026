"""
Information Gap Analysis and Next-Best-Action Ranking.
Formula:
priority = (financial_relevance * attribution_potential * evidence_quality * expected_info_gain) / investigation_cost
"""

from typing import List
from pydantic import BaseModel

class ActionRecommendation(BaseModel):
    action_id: str
    action_title: str
    target_entity: str
    information_gain: float
    estimated_cost: float
    priority_score: float
    description: str

def rank_next_actions(
    financial_relevance: float,
    attribution_potential: float,
    evidence_quality: float,
    case_status: str
) -> List[ActionRecommendation]:
    # Compute next actions
    actions = [
        ActionRecommendation(
            action_id="ACT-VASP-SUBPOENA",
            action_title="Serve Subpoena / LE Request to VASP Compliance",
            target_entity="DemoExchange Compliance",
            information_gain=0.95,
            estimated_cost=0.30,
            priority_score=round((financial_relevance * attribution_potential * evidence_quality * 0.95) / 0.30, 2),
            description="Request KYC record, login IP logs, and linked fiat bank account for deposit address."
        ),
        ActionRecommendation(
            action_id="ACT-BRIDGE-CORRELATION",
            action_title="Query Cross-Chain Relayer Logs",
            target_entity="Cross-Chain Bridge Relayer",
            information_gain=0.75,
            estimated_cost=0.40,
            priority_score=round((financial_relevance * attribution_potential * evidence_quality * 0.75) / 0.40, 2),
            description="Obtain message payload and destination validator signatures to verify minting transaction destination."
        ),
        ActionRecommendation(
            action_id="ACT-CLUSTER-MONITOR",
            action_title="Set Real-Time Cluster Alert on Downstream EOA",
            target_entity="Intermediary Cluster",
            information_gain=0.60,
            estimated_cost=0.15,
            priority_score=round((financial_relevance * attribution_potential * evidence_quality * 0.60) / 0.15, 2),
            description="Arm live mempool watcher for any outbound fund movements exceeding 0.1 ETH."
        )
    ]
    actions.sort(key=lambda a: a.priority_score, reverse=True)
    return actions
