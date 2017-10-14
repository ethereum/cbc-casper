"""The utils module ..."""
import casper.settings as s


def are_conflicting_estimates(estimate, possibly_conflicting_estimate):
    """Returns whether or there are conflicting estimates."""
    return not estimate.is_in_blockchain(possibly_conflicting_estimate)


def exists_free_message(estimate, val, sequence_num, view):
    """Returns whether there exists a free message.
    A free message is a message later than the sequence number from some val,
    and conflicts with the estimate."""
    
    curr_message = view.latest_messages[val]

    while curr_message.sequence_number >= sequence_num:
        if are_conflicting_estimates(estimate, curr_message):
            return True

        if curr_message.sequence_number == 0:
            break

        curr_message = curr_message.justification.latest_messages[val]

    return False


def get_weight(val_set):
    """Returns the weights of some set of validator names."""
    if not val_set:
        return 0

    return sum(s.WEIGHTS[v] for v in val_set)


def build_chain(tip, base):
    """Returns a list of blocks and blocks estimates from tip to base."""
    assert base is None or base.is_in_blockchain(tip), "expected tip & base to be in same chain"

    chain = []
    next_block = tip
    while next_block != base and next_block.estimate:
        chain.append((next_block, next_block.estimate))
        next_block = next_block.estimate

    return chain
