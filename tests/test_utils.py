import pytest
import random as r

import casper.settings as s
import casper.utils as utils


@pytest.mark.parametrize(
    'weights, expected_weight, validators',
    [
        ([i for i in range(10)], 45, None),
        ([i for i in range(9, -1, -1)], 45, None),
        ([r.random() for i in range(10)], None, None),
        ([i*2 for i in range(10)], 12, set([0, 1, 2, 3])),
        ([i*2 for i in range(10)], 12, [0, 1, 2, 3]),
    ]
)
def test_get_weight(weights, expected_weight, validators):
    s.update(weights)
    if expected_weight is None:
        expected_weight = sum(weights)
    if validators is None:
        validators = s.VALIDATOR_NAMES

    assert utils.get_weight(validators) == expected_weight


@pytest.mark.parametrize(
    'empty_param',
    [
        (None),
        (set()),
    ]
)
def test_get_weight_empty(empty_param):
    assert utils.get_weight(empty_param) == 0
