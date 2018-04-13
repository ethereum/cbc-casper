"""The testing utils module ... """
import pytest

from casper.validator_set import ValidatorSet
import casper.utils as utils


@pytest.mark.parametrize(
    'weights, subset, expected_weight',
    [
        ([i for i in range(10)], [i for i in range(10)], 45),
        ([i * 2 for i in range(10)], [0, 1, 2, 3], 12),
    ]
)
def test_get_weight(weights, subset, expected_weight, view, message):
    validator_set = ValidatorSet(weights, view, message)
    validators = validator_set.get_validators_by_names(subset)
    for validator in validator_set:
        print("Name: {}, Weight: {}".format(validator.name, validator.weight))

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
