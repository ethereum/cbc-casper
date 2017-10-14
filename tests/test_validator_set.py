import random as r
import pytest

from casper.validator_set import ValidatorSet


@pytest.mark.parametrize(
    'weights',
    [
        ({i: i for i in range(10)}),
        ({i: r.random() for i in range(10)}),
    ]
)
def test_new_validator_set(weights):
    vs = ValidatorSet(weights)

    assert len(vs.validators) == len(weights.keys())
    assert set(map(lambda v: v.weight, vs.validators)) == set(weights.values())


@pytest.mark.parametrize(
    'weights',
    [
        ({i: i for i in range(10)}),
        ({"name": 5, "cool": 1}),
    ]
)
def test_in(weights):
    vs = ValidatorSet(weights)

    for validator in vs.validators:
        assert validator in vs


@pytest.mark.parametrize(
    'weights',
    [
        ({i: i for i in range(10)}),
        ({"name": 5, "cool": 1}),
    ]
)
def test_len(weights):
    vs = ValidatorSet(weights)

    assert len(vs) == len(weights)


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
    vs = ValidatorSet(weights)

    assert vs.validator_names() == set(expected_names)


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
    vs = ValidatorSet(weights)

    assert vs.validator_weights() == set(expected_weights)


@pytest.mark.parametrize(
    'weights, expected_weight, validators',
    [
        ({i: i for i in range(10)}, 45, None),
        ({i: 9 - i for i in range(9, -1, -1)}, 45, None),
        ({i: r.random() for i in range(10)}, None, None),
        ({i: i*2 for i in range(10)}, 12, set([0, 1, 2, 3])),
        ({i: i*2 for i in range(10)}, 12, [0, 1, 2, 3]),
    ]
)
def test_weight(weights, expected_weight, validators):
    vs = ValidatorSet(weights)
    if expected_weight is None:
        expected_weight = sum(weights.values())

    assert round(vs.weight(validators), 2) == round(expected_weight, 2)


@pytest.mark.skip(reason="test not yet implemented")
def test_get_validator_by_name():
    pass


@pytest.mark.skip(reason="test not yet implemented")
def test_get_validators_by_names():
    pass
