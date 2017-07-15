from settings import ESTIMATE_SPACE


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
