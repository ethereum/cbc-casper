"""The forkchoice module implements the estimator function a blockchain"""


def get_max_weight_indexes(scores):
    """Returns the keys that map to the max value in a dict.
    The max value must be greater than zero."""

    max_score = max(scores.values())

    assert max_score != 0, "max_score of a block should never be zero"

    max_weight_estimates = {e for e in scores if scores[e] == max_score}

    return max_weight_estimates


def get_fork_choice(last_finalized_block, children, latest_messages):
    """Returns the estimate by selecting highest weight sub-trees.
    Starts from the last_finalized_block and stops when it reaches a tip."""

    scores = dict()

    for validator in latest_messages:
        current_block = latest_messages[validator]

        while current_block and current_block != last_finalized_block:
            scores[current_block] = scores.get(current_block, 0) + validator.weight
            current_block = current_block.estimate

    best_block = last_finalized_block
    while best_block in children:
        curr_scores = dict()
        max_score = 0
        for child in children[best_block]:
            curr_scores[child] = scores.get(child, 0)
            max_score = max(curr_scores[child], max_score)

        # We don't choose weight 0 children.
        # Also possible to make non-deterministic decision here.
        if max_score == 0:
            break

        max_weight_children = get_max_weight_indexes(curr_scores)

        assert len(max_weight_children) == 1, "... there should be no ties!"

        best_block = max_weight_children.pop()

    return best_block
