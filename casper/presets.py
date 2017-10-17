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
            sorted_validators = validator_set.sorted_by_name()
            sender_index = round_robin.next_sender_index
            round_robin.next_sender_index = (sender_index + 1) % len(validator_set)
            receiver_index = round_robin.next_sender_index

            return [[
                sorted_validators[sender_index],
                sorted_validators[receiver_index]
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
        rrob = message_maker("rrob")

        def no_final(validator_set):
            """Each round, two simultaneous round-robin message propagations occur at the same
            time. This results in validators never being able to finalize later blocks (they
            may finalize initial blocks, depending on validator weight distribution)."""
            return [rrob(validator_set)[0], rrob(validator_set)[0]]

        return no_final

    return None
