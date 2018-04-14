import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.validator_set import ValidatorSet

from simulations.utils import (
    generate_random_gaussian_weights,
    str2bool
)


@pytest.mark.parametrize(
    'num_validators, mu, sigma, min_weight',
    [
        (5, 60, 40, 20),
        (2, 50, 20, 10),
        (40, 50, 50, 10),
        (40, 50, 0, 10),
    ]
)
def test_generate_random_gaussian_weights(
        num_validators,
        mu,
        sigma,
        min_weight
        ):
    weights = generate_random_gaussian_weights(
        num_validators,
        mu,
        sigma,
        min_weight
    )

    assert len(weights) == num_validators
    assert min(weights) >= min_weight
    assert len(set(weights)) == num_validators, "Weights should be unique."


@pytest.mark.parametrize(
    'string, result',
    [
        ('true', True),
        ('t', True),
        ('yes', True),
        ('True', True),
        ('false', False),
        ('f', False),
        ('no', False),
        ('False', False)
    ]
)
def test_str2bool(string, result):
    assert str2bool(string) == result
