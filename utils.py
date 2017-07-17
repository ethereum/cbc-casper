from settings import ESTIMATE_SPACE, WEIGHTS
import random as r


def get_max_weight_estimates(scores):

    max_score = 0
    max_score_estimate = None
    for e in scores.keys():
        if max_score == 0:
            max_score = scores[e]

        if scores[e] > max_score:
            max_score = scores[e]

    max_weight_estimates = set()

    for e in scores.keys():
        if scores[e] == max_score:
            max_weight_estimates.add(e)

    return max_weight_estimates


def get_estimate_from_latest_bets(latest_bets, default=None):
    estimates = []
    for v in latest_bets:
        if latest_bets[v].estimate not in estimates:
            estimates.append(latest_bets[v].estimate)

    scores = dict()
    for e in estimates:
        scores[e] = 0

    for v in latest_bets:
        scores[latest_bets[v].estimate] += WEIGHTS[v]

    mwe = get_max_weight_estimates(scores)

    if default is not None:
        if default in mwe:
            return default

    if mwe == set():
        mwe = ESTIMATE_SPACE

    return r.choice(tuple(mwe))
