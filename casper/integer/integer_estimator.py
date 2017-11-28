"""The integer estimator module implements the estimator function integer consensus"""


def get_estimate_from_latest_messages(latest_bets):
    """Picks the median weight estimate given some latest bets."""

    sorted_bets = sorted(latest_bets.values(), key=lambda bet: bet.estimate)
    half_seen_weight = sum(v.weight for v in latest_bets) / 2.0

    assert half_seen_weight > 0

    total_estimate_weight = 0
    for bet in sorted_bets:
        total_estimate_weight += bet.sender.weight
        if total_estimate_weight >= half_seen_weight:
            return bet.estimate
