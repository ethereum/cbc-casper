"""The validator set testing module ... """

import random as r
import pytest
import itertools

from casper.validator_set import ValidatorSet


@pytest.mark.parametrize(
    'weights',
    [
        ({i: i for i in range(10)}),
        ({i: r.random() for i in range(10)}),
    ]
)
def test_new_validator_set(weights):
    val_set = ValidatorSet(weights)

    assert len(val_set.validators) == len(weights.keys())
    assert set(map(lambda v: v.weight, val_set.validators)) == set(weights.values())


@pytest.mark.parametrize(
    'weights',
    [
        ({i: i for i in range(10)}),
        ({"name": 5, "cool": 1}),
    ]
)
def test_in(weights):
    val_set = ValidatorSet(weights)

    for validator in val_set.validators:
        assert validator in val_set


@pytest.mark.parametrize(
    'weights',
    [
        ({i: i for i in range(10)}),
        ({"name": 5, "cool": 1}),
    ]
)
def test_len(weights):
    val_set = ValidatorSet(weights)

    assert len(val_set) == len(weights)


@pytest.mark.parametrize(
    'weights, expected_names',
    [
        ({i: i for i in range(10)}, list(range(10))),
        ({i: 9 - i for i in range(9, -1, -1)}, list(range(10))),
        (
            {str(i): r.random() for i in range(10)},
            map(lambda i: str(i), range(10))
        ),
    ]
)
def test_validator_names(weights, expected_names):
    val_set = ValidatorSet(weights)

    assert val_set.validator_names() == set(expected_names)


@pytest.mark.parametrize(
    'weights, expected_weights',
    [
        ({i: i for i in range(10)}, list(range(10))),
        ({i: 9 - i for i in range(9, -1, -1)}, list(range(10))),
        (
            {"one": 0, "two": 10, "three": 1000},
            [0, 10, 1000]
        ),
    ]
)
def test_validator_weights(weights, expected_weights):
    val_set = ValidatorSet(weights)

    assert val_set.validator_weights() == set(expected_weights)


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
def test_weight(weights, expected_weight, validator_names):
    val_set = ValidatorSet(weights)
    if expected_weight is None:
        expected_weight = sum(weights.values())

    if validator_names:
        validators = val_set.get_validators_by_names(validator_names)
    else:
        validators = None

    assert round(val_set.weight(validators), 2) == round(expected_weight, 2)


@pytest.mark.parametrize(
    'weights',
    [
        ({i: i for i in range(10)}),
        ({i: 9 - i for i in range(9, -1, -1)}),
        ({i: r.random() for i in range(10)}),
        ({i: i*2 for i in range(10)}),
        ({i: i*2 for i in range(10)}),
    ]
)
def test_get_validator_by_name(weights):
    val_set = ValidatorSet(weights)

    for validator in val_set:
        returned_val = val_set.get_validator_by_name(validator.name)
        assert validator == returned_val



@pytest.mark.parametrize(
    'weights',
    [
        ({i: i for i in range(10)}),
        ({i: 9 - i for i in range(9, -1, -1)}),
        ({i: r.random() for i in range(10)}),
        ({i: i*2 for i in range(10)}),
        ({i: i*2 for i in range(10)}),
    ]
)
def test_get_validators_by_names(weights):
    val_set = ValidatorSet(weights)

    for i in range(1, len(weights)):
        val_subsets = itertools.combinations(val_set, i)
        for subset in val_subsets:
            subset = {val for val in subset}
            val_names = {validator.name for validator in subset}
            returned_set = val_set.get_validators_by_names(val_names)

            assert subset == returned_set
