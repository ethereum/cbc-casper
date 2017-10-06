import settings as s
import random as r
import itertools


def message_maker(mode):

    if mode == "rand":
        pairs = list(itertools.permutations(range(s.NUM_VALIDATORS), 2))
        def random():
            return r.sample(pairs, s.NUM_MESSAGES_PER_ROUND)

        return random

    if mode == "rrob":
        msg = [0, 1]
        def round_robin():
            to_return = [[msg[0], msg[1]]]
            msg[0] = (msg[0] + 1) % s.NUM_VALIDATORS
            msg[1] = (msg[1] + 1) % s.NUM_VALIDATORS
            return to_return

        return round_robin

    if mode == "full":
        pairs = list(itertools.permutations(range(s.NUM_VALIDATORS), 2))
        def full_propagation():
            return pairs

        return full_propagation

    if mode == "nofinal":
        # depending on val weights, this message prop order could never finalize a block
        msg = [0, 1]
        def no_final():
            to_return = [[msg[0], msg[1]]]
            msg[0] = (msg[0] + 1) % s.NUM_VALIDATORS
            msg[1] = (msg[1] + 1) % s.NUM_VALIDATORS
            to_return.append([msg[0], msg[1]])
            return to_return

        return no_final

    return None
