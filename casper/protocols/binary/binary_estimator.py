"""The forkchoice module implements the estimator function a blockchain"""
import random as r


def get_estimate_from_latest_messages(latest_bets, default=None):
    """Picks the highest weight estimate (0 or 1) given some latest bets."""

    zero_weight = sum(v.weight for v in latest_bets if latest_bets[v].estimate == 0)
    one_weight = sum(v.weight for v in latest_bets if latest_bets[v].estimate == 1)

    if zero_weight > one_weight:
        return 0
    elif zero_weight < one_weight:
        return 1
    elif zero_weight == 0:
        return r.randint(0, 1)
    else:
        raise Exception("Should be no ties!")
