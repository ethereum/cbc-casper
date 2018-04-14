"""The binary estimator testing module tests the binary estimator"""
import pytest

from casper.protocols.binary.binary_protocol import BinaryProtocol
from casper.protocols.binary.bet import Bet
from casper.validator_set import ValidatorSet
import casper.protocols.integer.integer_estimator as estimator


@pytest.mark.parametrize(
    'weights, latest_estimates, estimate',
    [
        (
            [1],
            {0: 1},
            1
        ),
        (
            [5, 6, 7],
            {0: 0, 1: 0, 2: 1},
            0
        ),
        (
            [5, 10, 14],
            {0: 1, 1: 1, 2: 0},
            1
        ),
        (
            [5, 11],
            {0: 0, 1: 1},
            1
        ),
    ]
)
def test_estimator_picks_correct_estimate(weights, latest_estimates, estimate, create_binary_validator_set):
    validator_set = create_binary_validator_set(weights)
    latest_messages = dict()
    for val_name in latest_estimates:
        validator = validator_set.get_validator_by_name(val_name)
        latest_messages[validator] = Bet(
            latest_estimates[val_name], {}, validator, 1, 1
        )

    assert estimate == estimator.get_estimate_from_latest_messages(latest_messages)
