import pytest
import random as r

from casper.validator_set import ValidatorSet
import casper.utils as utils


@pytest.mark.parametrize(
    'weights, expected_weight, validator_names',
    [
        ({i: i for i in range(10)}, 45, None),
        ({i: 9 - i for i in range(9, -1, -1)}, 45, None),
        ({i: r.random() for i in range(10)}, None, None),
        ({i: i*2 for i in range(10)}, 12, set([0, 1, 2, 3])),
        ({i: i*2 for i in range(10)}, 12, [0, 1, 2, 3]),
    ]
)
def test_get_weight(weights, expected_weight, validator_names):
    validator_set = ValidatorSet(weights)
    if expected_weight is None:
        expected_weight = sum(weights.values())
    if validator_names is None:
        validators = validator_set.validators
    else:
        validators = validator_set.get_validators_by_names(validator_names)

    assert round(utils.get_weight(validators), 2) == round(expected_weight, 2)


@pytest.mark.parametrize(
    'empty_param',
    [
        (None),
        (set()),
    ]
)
def test_get_weight_empty(empty_param):
    assert utils.get_weight(empty_param) == 0
