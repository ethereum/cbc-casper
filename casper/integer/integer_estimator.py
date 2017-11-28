"""The integer estimator module implements the estimator function integer consensus"""


def get_estimate_from_latest_messages(latest_bets):
    """Picks the highest weight estimate (0 or 1) given some latest bets."""

    sorted_estimates = sorted(set(latest_bets[v].estimate for v in latest_bets))
    half_seen_weight = sum(v.weight for v in latest_bets) / 2

    assert sum(v.weight for v in latest_bets) > 0

    total_estimate_weight = 0
    for _, estimate in enumerate(sorted_estimates):
        estimate_weight = sum(
            v.weight for v in latest_bets
            if latest_bets[v].estimate == estimate
        )

        total_estimate_weight += estimate_weight
        if total_estimate_weight >= half_seen_weight:
            return estimate
