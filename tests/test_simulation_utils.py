import pytest

from casper.simulation_utils import (
    generate_random_validator_set
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
def test_generate_random_validator_set(
                                       num_validators,
                                       mu,
                                       sigma,
                                       min_weight
                                      ):
    vs = generate_random_validator_set(
        num_validators,
        mu,
        sigma,
        min_weight
    )

    assert len(vs.validators) == num_validators
    assert min(vs.validator_weights()) >= min_weight
    assert len(set(vs.validator_weights())) == num_validators, "Weights should be unique."
