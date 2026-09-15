"""
ATLAS Alternative Hypotheses generation.
"""

from typing import List
from backend.atlas.engine import AtlasHypothesis

def generate_alternatives() -> List[AtlasHypothesis]:
    return [
        AtlasHypothesis(
            hypothesis_id="ALT-1",
            title="Intermediate OTC / P2P Broker Cashing Out",
            explanation="Hop 1 could represent a peer-to-peer escrow settlement or OTC broker rather than a direct thief-controlled intermediary.",
            likelihood="Medium"
        ),
        AtlasHypothesis(
            hypothesis_id="ALT-2",
            title="Consolidation into Shared Liquidity Hot-Wallet",
            explanation="The terminal address might belong to a third-party non-custodial payment processor or swap aggregator rather than an individual customer deposit.",
            likelihood="Medium"
        ),
        AtlasHypothesis(
            hypothesis_id="ALT-3",
            title="Compromised Victim Private Key / Unauthorized Sweep",
            explanation="Transactions may originate from automated sweeper bots responding to compromised credentials, shifting attribution from deliberate transfer to sweeper-run sweep.",
            likelihood="Low"
        ),
        AtlasHypothesis(
            hypothesis_id="ALT-4",
            title="Collateralized DeFi Vault / Staking Contract",
            explanation="Transfers could represent automated margin collateral or liquidity provisioning into a protocol smart contract rather than a centralized custodian.",
            likelihood="Low"
        )
    ]
