"""The simulution utils module ... """
import random as r

from casper.networks import (
    ConstantDelayNetwork,
    GaussianDelayNetwork,
    LinearDelayNetwork,
    NoDelayNetwork,
    StepNetwork
)

from simulations.message_modes import (
    RandomMessageMode,
    RoundRobinMessageMode,
    FullMessageMode,
    NoFinalMessageMode,
)

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.protocols.binary.binary_protocol import BinaryProtocol
from casper.protocols.integer.integer_protocol import IntegerProtocol
from casper.protocols.order.order_protocol import OrderProtocol
from casper.protocols.concurrent.concurrent_protocol import ConcurrentProtocol
from casper.validator_set import ValidatorSet


SELECT_NETWORK = {
    'no-delay': NoDelayNetwork,
    'step': StepNetwork,
    'constant': ConstantDelayNetwork,
    'linear': LinearDelayNetwork,
    'gaussian': GaussianDelayNetwork
}

SELECT_PROTOCOL = {
    'blockchain': BlockchainProtocol,
    'binary': BinaryProtocol,
    'integer': IntegerProtocol,
    'order': OrderProtocol,
    'concurrent': ConcurrentProtocol
}

SELECT_MESSAGE_MODE = {
    'rand': RandomMessageMode,
    'rrob': RoundRobinMessageMode,
    'full': FullMessageMode,
    'nofinal': NoFinalMessageMode
}


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
