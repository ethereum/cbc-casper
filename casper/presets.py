"""The presets module ... """
import random as r
import itertools

import casper.settings as s


def message_maker(mode):
    """The message maker defines the logic for running each type of simulation."""

    if mode == "rand":

        def random(validator_set):
            """Each round, some randomly selected validators propagate their most recent
            message to other randomly selected validators, who then create new messages."""
            pairs = list(itertools.permutations(validator_set, 2))
            return r.sample(pairs, s.NUM_MESSAGES_PER_ROUND)

        return random

    if mode == "rrob":

        def round_robin(validator_set):
            """Each round, the creator of the last round's block sends it to the next
            receiver, who then creates a block."""
            sorted_names = sorted(list(validator_set.validator_names()))
            sender_index = round_robin.next_sender_index
            round_robin.next_sender_index = (sender_index + 1) % len(validator_set)
            receiver_index = round_robin.next_sender_index

            return [[
                validator_set.get_validator_by_name(sorted_names[sender_index]),
                validator_set.get_validator_by_name(sorted_names[receiver_index])
            ]]

        round_robin.next_sender_index = 0
        return round_robin

    if mode == "full":

        def full_propagation(validator_set):
            """Each round, all validators receive all other validators previous
            messages, and then all create messages."""
            pairs = list(itertools.permutations(validator_set, 2))
            return pairs

        return full_propagation

    if mode == "nofinal":
        msg = [0, 1]

        def no_final(validator_set):
            """Each round, two simultaneous round-robin message propagations occur at the same
            time. This results in validators never being able to finalize later blocks (they
            may finalize initial blocks, depending on validator weight distribution)."""
            to_return = [[msg[0], msg[1]]]
            msg[0] = (msg[0] + 1) % len(validator_set)
            msg[1] = (msg[1] + 1) % len(validator_set)
            to_return.append([msg[0], msg[1]])
            return to_return

        return no_final

    return None
