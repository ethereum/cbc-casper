import settings as s
import random as r


def message_maker(mode):
    if mode == "rand":

        pairs=[[i, j] for i in xrange(s.NUM_VALIDATORS) for j in xrange(s.NUM_VALIDATORS) if not i == j]
        def random():
            return r.sample(pairs, s.NUM_MESSAGES_PER_ROUND)

        return random

    if mode == "rrob":

        msg=[0, 1]
        def round_robin():
            to_return = [[msg[0], msg[1]]]
            msg[0] = (msg[0] + 1) % s.NUM_VALIDATORS
            msg[1] = (msg[1] + 1) % s.NUM_VALIDATORS
            return to_return

        return round_robin

    if mode == "full":

        pairs=[[i, j] for i in xrange(s.NUM_VALIDATORS) for j in xrange(s.NUM_VALIDATORS) if not i == j]
        def full_propagation():
            return pairs

        return full_propagation
