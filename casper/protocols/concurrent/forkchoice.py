"""The forkchoice module implements the estimator function a concurrent schedule"""

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

def get_outputs(blocks):
    outputs = set()

    for block in blocks:
        outputs.update(block.estimate[2])

    return outputs

def update_outputs(outputs, blocks):
    for block in blocks:
        for output in block.estimate[1]:
            outputs.remove(output)
        for output in block.estimate[2]:
            outputs.add(output)

# record of what blocks create what ouputs
def update_output_dict(output_dict, new_blocks):
    for block in new_blocks:
        for output in block.estimate[2]:
            assert output not in output_dict # only should be spent once...
            output_dict[output] = block

def is_consumable(block, current_blocks, scores, available_outputs):
    for other_block in current_blocks:
        if any(block.estimate[1].intersection(other_block.estimate[1])):
            if scores.get(block, 0) < scores.get(other_block, 0):
                return False
        # we can't eat a block if it's outputs are not yet available
        for output in block.estimate[1]:
            if output not in available_outputs:
                return False

    return True

def get_children(blocks, children):
    children_blocks = set()

    for block in blocks:
        if block in children:
            children_blocks.update(children[block])

    return children_blocks


def get_fork_choice(last_finalized_estimate, children, latest_messages):
    """Returns the estimate by selecting highest weight sub-trees.
    Starts from the last_finalized_estimate and stops when it reaches a tips."""
    output_dict = dict()
    available_outputs = set() # should initally start w/ all the stuff form the last finalized estimate...
    for block in last_finalized_estimate:
        available_outputs.update(block.estimate[1])

    scores = get_scores(latest_messages)

    current_blocks = last_finalized_estimate # this is a set of blocks
    update_output_dict(output_dict, current_blocks)
    update_outputs(available_outputs, current_blocks)
    current_children = get_children(current_blocks, children)

    while any(current_children):
        next_blocks = set()

        for block in current_children:
            if is_consumable(block, current_children, scores, available_outputs):
                next_blocks.add(block)

        current_blocks = next_blocks
        update_output_dict(output_dict, current_blocks)
        update_outputs(available_outputs, current_blocks)
        current_children = get_children(current_blocks, children)

    return available_outputs, output_dict
