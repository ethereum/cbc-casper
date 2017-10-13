"""The model utils module ... """
import casper.settings as s


def get_estimate_from_latest_messages(latest_bets, default=None):
    """This function has an invalid name & wrong documentation."""

    zero_weight = sum(s.WEIGHTS[v] for v in latest_bets if latest_bets[v].estimate == 0)
    one_weight = sum(s.WEIGHTS[v] for v in latest_bets if latest_bets[v].estimate == 1)

    if zero_weight > one_weight:
        return 0
    elif zero_weight < one_weight:
        return 1
    else:
        if zero_weight != 0:
            raise RuntimeError("...no two subsets of validators should have same weight")
        else:
            return default
