"""The simulution utils module ... """
import random as r

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.protocols.binary.binary_protocol import BinaryProtocol
from casper.protocols.integer.integer_protocol import IntegerProtocol
from casper.protocols.order.order_protocol import OrderProtocol
from casper.validator_set import ValidatorSet

from simulations.networks.simple_networks import (
    ConstantDelayNetwork,
    GaussianDelayNetwork,
    LinearDelayNetwork,
    NoDelayNetwork,
    StepNetwork
)


MESSAGE_MODES = ['rand', 'always']
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


def message_strategy(mode):
    """The message strategy defines the logic for a validator_client making a message."""

    if mode == "rand":

        def random():
            """each time asked, 10% chance of making message"""
            if r.random() <= 0.10:
                return True
            return False

        return random

    if mode == "always":

        def always():
            """Each time asked, 100% chance of making message"""
            return True

        return always

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
