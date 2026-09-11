"""
ATLAS Robustness Score calculation.
"""

def calculate_robustness(
    alternatives_count: int,
    contradictions_count: int,
    ml_rules_disagreement: bool = False
) -> float:
    robustness = max(0.20, 0.92 - (alternatives_count * 0.05) - (contradictions_count * 0.08))
    if ml_rules_disagreement:
        robustness = max(0.15, robustness - 0.20)
    return round(robustness, 2)
