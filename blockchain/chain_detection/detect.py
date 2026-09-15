"""
Chain detection module for VAJRA.
Identifies whether a cryptocurrency address is BTC (Bitcoin) or ETH (Ethereum)
based on address format, prefixes, and checksum rules.
"""

from __future__ import annotations
import re
from typing import Literal

SupportedChain = Literal["BTC", "ETH"]

# Regex for standard Ethereum hex address (40 hex chars prefixed by 0x)
ETH_ADDRESS_REGEX = re.compile(r"^0x[a-fA-F0-9]{40}$")

# Bitcoin address patterns:
# P2PKH: starts with '1', base58 (26-35 characters)
# P2SH: starts with '3', base58 (26-35 characters)
# Bech32 (SegWit / Taproot): starts with 'bc1', alphanumeric (bc1q... or bc1p..., 14-74 characters)
BTC_BASE58_REGEX = re.compile(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$")
BTC_BECH32_REGEX = re.compile(r"^bc1[a-z0-9]{11,71}$", re.IGNORECASE)


def is_valid_eth_address(address: str) -> bool:
    """Check if string is a valid Ethereum address format."""
    if not isinstance(address, str):
        return False
    return bool(ETH_ADDRESS_REGEX.match(address))


def is_valid_btc_address(address: str) -> bool:
    """Check if string is a valid Bitcoin address format (Legacy, P2SH, or Bech32)."""
    if not isinstance(address, str):
        return False
    if BTC_BASE58_REGEX.match(address):
        return True
    if BTC_BECH32_REGEX.match(address):
        return True
    return False


def detect_chain(address: str) -> SupportedChain:
    """
    Detect the blockchain for a given wallet address.
    
    Raises:
        ValueError: If address does not match BTC or ETH format.
    """
    if not address or not isinstance(address, str):
        raise ValueError("Address must be a non-empty string.")

    cleaned_address = address.strip()

    if is_valid_eth_address(cleaned_address):
        return "ETH"

    if is_valid_btc_address(cleaned_address):
        return "BTC"

    raise ValueError(
        f"Unsupported or invalid address format for '{address}'. VAJRA live scope is restricted to BTC and ETH."
    )
