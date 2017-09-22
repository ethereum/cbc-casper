import settings as s

def get_later_messages_from_val(val, sequence_num, most_recent_message):
    later_messages = set()

    assert most_recent_message.sender == val, "...expected validator to be the same!"

    curr = most_recent_message

    while curr.sequence_number > sequence_num:
        later_messages.add(curr)
        curr = curr.justification.latest_messages[val]

    return later_messages


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
