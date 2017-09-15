import settings as s
import random as r
import copy


def get_max_weight_indexes(scores):

    max_score = max(scores.values())

    max_weight_estimates = {e for e in scores.keys() if scores[e] == max_score}

    return max_weight_estimates


def get_fork_choice(last_finalized_block, children, latest_messages):
    v_curr_chain = dict()

    for v in latest_messages.keys():
        if last_finalized_block is None or last_finalized_block.is_in_blockchain(latest_messages[v]):
            v_curr_chain[v] = build_chain(latest_messages[v], last_finalized_block)

    scores = dict()

    for v in v_curr_chain.keys():
        current_block = latest_messages[v]

        while current_block != last_finalized_block:
            scores[current_block] = scores.get(current_block, 0) + s.WEIGHTS[v]
            current_block = current_block.estimate

    best_block = last_finalized_block
    while best_block in children.keys():
        curr_scores = dict()
        for child in children[best_block]:
            curr_scores[child] = scores.get(child, 0)

        max_weight_children = get_max_weight_indexes(curr_scores)

        assert len(max_weight_children) == 1, "... there should be no ties!"

        best_block = max_weight_children.pop()

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
        scores[latest_bets[v].estimate] += s.WEIGHTS[v]

    mwe = get_max_weight_estimates(scores)

    if default is not None:
        if default in mwe:
            return default

    if mwe == set():
        mwe = s.ESTIMATE_SPACE

    return r.choice(tuple(mwe))


def build_chain(tip, base):
    #assert base.is_in_blockchain(tip), "expected tip to be in same blockchain as base"

    chain = []
    next_block = tip
    while next_block != base and next_block.estimate is not None :
        chain.append((next_block, next_block.estimate))
        next_block = next_block.estimate

    return chain
