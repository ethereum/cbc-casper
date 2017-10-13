"""The presets module ... """
import random as r
import itertools

import casper.settings as s


def message_maker(mode):
    """The message maker defines the logic for running each type of simulation."""
    if mode == "rand":
        pairs = list(itertools.permutations(range(s.NUM_VALIDATORS), 2))
        def random():
            """Each round, some randomly selected validators propagate their most recent
            message to other randomly selected validators, who then create new messages."""
            return r.sample(pairs, s.NUM_MESSAGES_PER_ROUND)

        return random

    if mode == "rrob":
        msg = [0, 1]
        def round_robin():
            """Each round, the creator of the last round's block sends it to the next
            receiver, who then creates a block."""
            to_return = [[msg[0], msg[1]]]
            msg[0] = (msg[0] + 1) % s.NUM_VALIDATORS
            msg[1] = (msg[1] + 1) % s.NUM_VALIDATORS
            return to_return

        return round_robin

    if mode == "full":
        pairs = list(itertools.permutations(range(s.NUM_VALIDATORS), 2))
        def full_propagation():
            """Each round, all validators receive all other validators previous
            messages, and then all create messages."""
            return pairs

        return full_propagation

    if mode == "nofinal":
        msg = [0, 1]
        def no_final():
            """Each round, two simultaneous round-robin message propagations occur at the same
            time. This results in validators never being able to finalize later blocks (they
            may finalize initial blocks, depending on validator weight distribution)."""
            to_return = [[msg[0], msg[1]]]
            msg[0] = (msg[0] + 1) % s.NUM_VALIDATORS
            msg[1] = (msg[1] + 1) % s.NUM_VALIDATORS
            to_return.append([msg[0], msg[1]])
            return to_return

        return no_final

    return None
