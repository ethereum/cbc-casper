import settings as s
import random as r
import copy
import utils


def get_max_weight_indexes(scores):

    max_score = max(scores.values())

    max_weight_estimates = {e for e in scores.keys() if scores[e] == max_score}

    return max_weight_estimates


def get_fork_choice(last_finalized_block, children, latest_messages):
    v_curr_chain = dict()

    for v in latest_messages.keys():
        if last_finalized_block is None or last_finalized_block.is_in_blockchain(latest_messages[v]):
            v_curr_chain[v] = utils.build_chain(latest_messages[v], last_finalized_block)

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
