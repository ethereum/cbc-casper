def get_estimate_from_latest_messages(latest_bets):
    """Picks the highest weight estimate (0 or 1) given some latest bets."""

    sample_list = list(latest_bets.values())[0].estimate
    elem_weights = {elem: 0 for elem in sample_list}
    for bet in latest_bets:
        sender = bet.sender
        estimate = bet.estimate
        for i, elem in enumerate(estimate):
            elem_weights[elem] += sender.weight * (len(estimate) - i)

    return sorted(elem_weights, key=lambda elem: elem_weights[elem])
