from settings import ESTIMATE_SPACE, WEIGHTS
import random as r


def get_max_weight_estimates(scores):

    max_score = 0
    max_score_estimate = None
    for e in ESTIMATE_SPACE:
        if max_score == 0:
            max_score = scores[e]

        if scores[e] > max_score:
            max_score = scores[e]

    max_weight_estimates = set()

    for e in ESTIMATE_SPACE:
        if scores[e] == max_score:
            max_weight_estimates.add(e)

    return max_weight_estimates


def get_estimate_from_justification(justification, default=None):
    scores = dict()
    for e in ESTIMATE_SPACE:
        scores[e] = 0

    for v in justification:
        scores[justification[v].estimate] += WEIGHTS[v]

    mwe = get_max_weight_estimates(scores)

    if default is not None:
        assert default in ESTIMATE_SPACE, "expected default to be an estimate"
        if default in mwe:
            return default

    return r.choice(tuple(mwe))
