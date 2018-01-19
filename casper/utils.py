"""The utils module contains functions for safety oracles and plotting"""


def exists_free_message(estimate, val, sequence_num, view):
    """Returns whether there exists a free message.
    A free message is a message later than the sequence number from some val,
    and conflicts with the estimate."""

    curr_message = view.latest_messages[val]

    while curr_message.sequence_number >= sequence_num:
        if estimate.conflicts_with(curr_message):
            return True

        if curr_message.sequence_number == 0:
            break

        next_message_hash = curr_message.justification[val]
        curr_message = view.justified_messages[next_message_hash]

    return False


def get_weight(val_set):
    """Returns the weights of some set of validator names."""
    if not val_set:
        return 0

    return sum(v.weight for v in val_set)


def edge(edges, width, color, style):
    """Builds an edge to display"""
    return {
        'edges': edges,
        'width': width,
        'edge_color': color,
        'style': style
    }


def build_chain(tip, base):
    """Returns a list of blocks and blocks estimates from tip to base."""
    assert base is None or base.is_in_blockchain(tip), "expected tip & base to be in same chain"

    chain = []
    next_block = tip
    while next_block != base:
        chain.append((next_block, next_block.estimate))
        next_block = next_block.estimate

    return chain


def build_schedule(tip):
    """Returns a list of blocks and blocks estimates from tip to base."""
    stack = [block for block in tip]
    schedule = []

    while any(stack):
        curr_block = stack.pop()

        if curr_block is None:
            continue

        for ancestor in curr_block.estimate['blocks']:
            if ancestor is None:
                continue
            schedule.append((curr_block, ancestor))
            stack.append(ancestor)

    return schedule
