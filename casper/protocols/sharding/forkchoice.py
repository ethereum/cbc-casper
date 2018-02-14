"""The forkchoice module implements the estimator function a blockchain"""


def get_max_weight_indexes(scores):
    """Returns the keys that map to the max value in a dict.
    The max value must be greater than zero."""

    max_score = max(scores.values())

    assert max_score != 0, "max_score of a block should never be zero"

    max_weight_estimates = {e for e in scores if scores[e] == max_score}

    return max_weight_estimates


def get_scores(starting_block, latest_messages, shard_id):
    """Returns a dict of block => weight"""
    scores = dict()

    for validator, current_block in latest_messages.items():
        if not current_block.on_shard(shard_id):
            continue

        while current_block and current_block != starting_block:
            scores[current_block] = scores.get(current_block, 0) + validator.weight
            current_block = current_block.prev_block(shard_id)

    return scores


def get_shard_fork_choice(starting_block, children, latest_messages, shard_id):
    """Get the forkchoice for a specific shard"""

    scores = get_scores(starting_block, latest_messages, shard_id)

    best_block = starting_block
    while best_block in children:
        curr_scores = dict()
        max_score = 0
        for child in children[best_block]:
            if not child.on_shard(shard_id):
                continue  # we only select children on the same shard
            curr_scores[child] = scores.get(child, 0)
            max_score = max(curr_scores[child], max_score)

        # If no child on shard, or 0 weight block, stop
        if max_score == 0:
            break

        max_weight_children = get_max_weight_indexes(curr_scores)

        assert len(max_weight_children) == 1, "... there should be no ties!"

        best_block = max_weight_children.pop()

    return best_block


def get_all_shards_fork_choice(starting_blocks, children, latest_messages_on_shard):
    """Returns a dict of shard_id -> forkchoice.
    Starts from starting block for shard, and stops when it reaches tip"""

    # for any shard we have latest messages on, we should have a starting block
    for key in starting_blocks.keys():
        assert key in latest_messages_on_shard
    for key in latest_messages_on_shard.keys():
        assert key in latest_messages_on_shard

    shards_forkchoice = {
        shard_id: get_shard_fork_choice(
            starting_blocks[shard_id],
            children,
            latest_messages_on_shard[shard_id],
            shard_id
        ) for shard_id in starting_blocks
    }

    return shards_forkchoice
