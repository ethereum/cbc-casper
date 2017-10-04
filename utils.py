import settings as s

def are_conflicting_estimates(estimate, possibly_conflicting_estimate):
    return not estimate.is_in_blockchain(possibly_conflicting_estimate)


def exists_free_message(estimate, val, sequence_num, view):
    curr_message = view.latest_messages[val]

    while curr_message.sequence_number >= sequence_num:
        if are_conflicting_estimates(estimate, curr_message):
            return True

        if curr_message.sequence_number == 0:
            break

        curr_message = curr_message.justification.latest_messages[val]

    return False


def get_weight(val_set):
    if val_set is None:
        return 0

    return sum(s.WEIGHTS[v] for v in val_set)


def build_chain(tip, base):
    assert base is None or base.is_in_blockchain(tip), "expected tip to be in same blockchain as base"

    chain = []
    next_block = tip
    while next_block != base and next_block.estimate is not None :
        chain.append((next_block, next_block.estimate))
        next_block = next_block.estimate

    return chain
