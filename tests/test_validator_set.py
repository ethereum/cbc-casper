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

    assert vs.weight(validators) == expected_weight
