"""test order estimator"""
import pytest

from casper.order.bet import Bet
from casper.validator_set import ValidatorSet
from casper.justification import Justification
import casper.order.order_estimator as estimator


@pytest.mark.parametrize(
    'weights, latest_estimates, estimate',
    [
        (
            {0: 5},
            {0: [1, 5, 6]},
            [1, 5, 6]
        ),
        (
            {0: 5, 1: 6, 2: 7},
            {
                0: [1, 2],
                1: [1, 2],
                2: [2, 1]
            },
            [1, 2]
        ),
        (
            {0: 5, 1: 6, 2: 7},
            {
                0: [1, 2, 3],
                1: [2, 3, 1],
                2: [2, 1, 3]
            },  # {2: 31, 1: 16, 3: 6}
            [2, 1, 3]
        ),
        (
            {0: 5, 1: 10, 2: 14},
            {
                0: ["fish", "pig", "horse", "dog"],
                1: ["dog", "horse", "pig", "fish"],
                2: ["pig", "horse", "fish", "dog"]
            },  # {"fish": 29, "pig": 62, "horse": 53, "dog": 30}
            ["pig", "horse", "dog", "fish"]
        ),
        (
            {0: 5, 1: 6, 2: 7, 3: 8},
            {
                0: ["fish", "pig", "horse"],
                1: ["horse", "pig", "fish"],
                2: ["pig", "horse", "fish"],
                3: ["fish", "horse", "pig"]
            },  # {"fish": 26, "pig": 25, "horse": 27}
            ["horse", "fish", "pig"]
        ),

    ]
)
def test_estimator_picks_correct_estimate(weights, latest_estimates, estimate):
    validator_set = ValidatorSet(weights)

    latest_messages = dict()
    for val_name in latest_estimates:
        validator = validator_set.get_validator_by_name(val_name)
        latest_messages[validator] = Bet(
            latest_estimates[val_name], Justification(), validator
        )

    assert estimate == estimator.get_estimate_from_latest_messages(latest_messages)
