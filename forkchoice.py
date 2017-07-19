from settings import ESTIMATE_SPACE, WEIGHTS, VALIDATOR_NAMES
import random as r


def get_max_weight_indexes(scores):

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


def get_favorite_child_of_block(block, children, latest_messages):

    scores = dict()
    for b in children[block]:
        scores[b] = 0

    memo = set()
    for b in children[block]:
        for v in latest_messages.keys():
            if v in memo:
                continue
            if latest_messages[v].is_decendant(latest_messages[v]):
                scores[b] += WEIGHTS[v]

    max_weight_children = get_max_weight_indexes(scores)

    c = r.choice(tuple(max_weight_children))
    print "c:", c
    return c


def get_fork_choice(last_finalized_block, children, latest_messages):

    best_block = last_finalized_block
    while(best_block in children.keys()):
        best_block = get_favorite_child_of_block(best_block, children, latest_messages)

    return best_block


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
