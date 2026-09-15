"""
Priority scoring and ranking for trace paths.
Priority = confidence + financial relevance + attribution potential.
"""

def compute_path_priority(confidence: float, amount: float, origin_amount: float, hops: int, touches_terminal: bool) -> float:
    financial_relevance = min(1.0, amount / max(origin_amount, 0.0001))
    attribution_potential = 1.0 if touches_terminal else max(0.1, 1.0 - (hops * 0.12))
    score = (confidence * 0.4) + (financial_relevance * 0.35) + (attribution_potential * 0.25)
    return round(score, 4)
