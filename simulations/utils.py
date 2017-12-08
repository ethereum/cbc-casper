"""The simulution utils module ... """
import random as r

from casper.networks import (
    ConstantDelayNetwork,
    GaussianDelayNetwork,
    LinearDelayNetwork,
    NoDelayNetwork,
    StepNetwork
)
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.protocols.binary.binary_protocol import BinaryProtocol
from casper.protocols.integer.integer_protocol import IntegerProtocol
from casper.protocols.order.order_protocol import OrderProtocol
from casper.validator_set import ValidatorSet

MESSAGE_MODES = ['rand', 'rrob', 'full', 'nofinal']
NETWORKS = ['no-delay', 'step', 'constant', 'linear', 'gaussian']
PROTOCOLS = ['blockchain', 'binary', 'integer', 'order']


def select_network(network):
    if network == 'no-delay':
        return NoDelayNetwork
    if network == 'constant':
        return ConstantDelayNetwork
    if network == 'step':
        return StepNetwork
    if network == 'linear':
        return LinearDelayNetwork
    if network == 'gaussian':
        return GaussianDelayNetwork


def select_protocol(protocol):
    if protocol == 'blockchain':
        return BlockchainProtocol
    if protocol == 'binary':
        return BinaryProtocol
    if protocol == 'order':
        return OrderProtocol
    if protocol == 'integer':
        return IntegerProtocol


def message_maker(mode):
    """The message maker defines the logic for running each type of simulation."""

    if mode == "rand":

        def random(validator_set, num_messages=1):
            """Each round, some randomly selected validator makes a message"""
            return r.sample(validator_set.validators, 1)
            # pairs = list(itertools.permutations(validator_set, 2))
            # return r.sample(pairs, num_messages)

        return random

    if mode == "rrob":

        def round_robin(validator_set):
            """Each round, the next validator in a set order makes a message"""
            sorted_validators = validator_set.sorted_by_name()
            sender_index = round_robin.next_sender_index
            round_robin.next_sender_index = (sender_index + 1) % len(validator_set)
            # receiver_index = round_robin.next_sender_index

            return [sorted_validators[sender_index]]

        round_robin.next_sender_index = 0
        return round_robin

    if mode == "full":

        def full_propagation(validator_set):
            """Each round, all validators make all messages"""
            return validator_set.validators

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


def generate_random_gaussian_validator_set(
        protocol,
        num_validators=5,
        mu=60,
        sigma=40,
        min_weight=20
        ):
    """Generates a random validator set."""

    # Give the validators random weights in 0.,BIGINT;
    # this "big" integer's job is to guarantee the "tie-breaking property"
    # that no two subsets of validator's total weights are exactly equal.
    # In prod, we will add a random epsilon to weights given by bond amounts,
    # however, for the purposes of the current work, this will suffice.
    BIGINT = 1000000000000

    names = set(range(num_validators))
    weights = {
        i: max(min_weight, r.gauss(mu, sigma))
        + 1.0/(BIGINT + r.uniform(0, 1)) + r.random()
        for i in names
    }

    return ValidatorSet(weights, protocol)


def validator_generator(config, protocol):
    if config['gen_type'] == 'gauss':

        def gauss_generator():
            return generate_random_gaussian_validator_set(
                protocol,
                config['num_validators'],
                config['mu'],
                config['sigma'],
                config['min_weight']
            )

        return gauss_generator

    if config['gen_type'] == 'weights':
        jitter_weights = {
            i: weight + r.random()
            for i, weight in enumerate(config['weights'])
        }

        def weights_generator():
            return ValidatorSet(jitter_weights, protocol)

        return weights_generator
