"""The forkchoice module implements the estimator function a concurrent schedule"""


def get_descendants(blocks, children, to_avoid=None):
    print("calling get_descendants with blocks {} and children {}".format(blocks, children))

    if not to_avoid:
        to_avoid = set()

    descendants = set()
    stack = [block for block in blocks]

    while any(stack):
        curr_block = stack.pop()
        add = True

        for block in to_avoid:
            if block.is_in_history(curr_block):
                add = False

        if add:
            descendants.add(curr_block)
            for b in children.get(curr_block, set()):
                stack.append(b)

    return descendants


def get_conflicting_block_sets(possible_blocks):
    conflicting_block_sets = set()

    for block in possible_blocks:
        conflicting_blocks = set([block])
        for other_block in possible_blocks:
            if block == other_block:
                continue
            if any(block.estimate[1].intersection(other_block.estimate[1])):
                conflicting_blocks.add(other_block)

        if len(conflicting_blocks) > 1:
            immut_set = frozenset(b for b in conflicting_blocks)
            conflicting_block_sets.add(immut_set)

    return conflicting_block_sets


def get_blocks_to_avoid(conflicting_block_sets, scores):
    block_to_avoid = set()

    for conflicting_blocks in conflicting_block_sets:
        best_block = max(conflicting_blocks, key=lambda b: scores.get(b, 0))
        block_to_avoid.update(conflicting_blocks.difference({best_block}))

    return block_to_avoid

def get_ancestors(block):
    ancestors = set()
    stack = [block]

    while any(stack):
        curr_block = stack.pop()

        if curr_block is None:
            continue

        if curr_block not in ancestors:
            ancestors.add(curr_block)
            stack.extend([b for b in curr_block.estimate[0]])

    return ancestors

def get_scores(latest_messages):
    scores = dict()

    for validator in latest_messages:
        ancestors = get_ancestors(latest_messages[validator])
        for b in ancestors:
            scores[b] = scores.get(b, 0) + validator.weight

    return scores


def get_fork_choice(last_finalized_estimate, children, latest_messages):
    """Returns the estimate by selecting highest weight sub-trees.
    Starts from the last_finalized_estimate and stops when it reaches a tips."""
    # this is horribly inefficient!

    print("Called forkchoice with last_finalized_estimate {}, and children {}, and latest messages {}".format(last_finalized_estimate, children, latest_messages))

    all_descendants = get_descendants(last_finalized_estimate, children)
    print("all_descendants {} ".format(all_descendants))

    conflicting_block_sets = get_conflicting_block_sets(all_descendants)
    scores = get_scores(latest_messages)
    print("scores {}".format(scores))
    print("conflicting_block_sets {} ".format(conflicting_block_sets))
    for sets in conflicting_block_sets:
        for block in sets:
            print(block.estimate[1])

    blocks_to_avoid = get_blocks_to_avoid(conflicting_block_sets, scores)
    print("blocks to avoid {} ".format(blocks_to_avoid))

    select_descendants = get_descendants(last_finalized_estimate, children, blocks_to_avoid)
    print("select_descendants {} ".format(select_descendants))

    tips = {block for block in select_descendants if block not in children} # this means they are tips!
    print("tips {} ".format(tips))

    return tips


def get_available_inputs(tip):
    # note: this is horribly inefficient; as they say, don't optimize to soon :)
    all_inputs = set()
    eaten = set()

    all_ancestors = set()

    for b in tip:
        all_ancestors.update(get_ancestors(b))

    for b in all_ancestors:
        all_inputs.update(b.estimate[1])
        all_inputs.update(b.estimate[2])
        eaten.update(b.estimate[1])

    return all_inputs - eaten
