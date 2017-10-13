import pytest
import random as r

from casper.validator_set import ValidatorSet


@pytest.mark.parametrize(
    'weights, expected_weight, validators',
    [
        ({i: i for i in xrange(10)}, 45, None),
        ({i: 9 - i for i in xrange(9, -1, -1)}, 45, None),
        ({i: r.random() for i in xrange(10)}, None, None),
        ({i: i*2 for i in xrange(10)}, 12, set([0, 1, 2, 3])),
        ({i: i*2 for i in xrange(10)}, 12, [0, 1, 2, 3]),
    ]
)
def test_weight(weights, expected_weight, validators):
    vs = ValidatorSet(weights)
    if expected_weight is None:
        expected_weight = sum(weights.values())

    assert vs.weight(validators) == expected_weight
