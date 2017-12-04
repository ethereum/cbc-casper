"""The block testing module ..."""
import pytest

from casper.protocols.integer.bet import Bet
from casper.validator_set import ValidatorSet
import casper.protocols.integer.integer_estimator as estimator


@pytest.mark.parametrize(
    'weights, latest_estimates, estimate',
    [
        (
            {0: 5},
            {0: 5},
            5
        ),
        (
            {0: 5, 1: 6, 2: 7},
            {0: 5, 1: 5, 2: 5},
            5
        ),
        (
            {0: 5, 1: 10, 2: 14},
            {0: 0, 1: 5, 2: 10},
            5
        ),
        (
            {0: 5, 1: 11},
            {0: 0, 1: 6},
            6
        ),
        (
            {0: 5, 1: 10, 2: 14},
            {0: 0, 1: 0, 2: 1},
            0
        ),
        (
            {0: 5, 1: 5},
            {0: 0, 1: 1},
            0
        ),
    ]
)
def test_estimator_picks_correct_estimate(weights, latest_estimates, estimate, empty_just):
    validator_set = ValidatorSet(weights)

    latest_messages = dict()
    for val_name in latest_estimates:
        validator = validator_set.get_validator_by_name(val_name)
        latest_messages[validator] = Bet(
            latest_estimates[val_name], empty_just, validator, 1, 1
        )

    assert estimate == estimator.get_estimate_from_latest_messages(latest_messages)
