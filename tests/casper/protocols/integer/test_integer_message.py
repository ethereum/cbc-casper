import pytest

from casper.protocols.integer.bet import Bet
from casper.protocols.integer.integer_view import IntegerView

@pytest.mark.parametrize(
    'estimate, is_valid',
    [
        (0, True),
        (1, True),
        (10000000, True),
        (-10000000, True),
        (True, True),
        (False, True),
        ((0, 1), False),
        (None, False),
    ]
)
def test_accepts_valid_estimates(estimate, is_valid):
    assert Bet.is_valid_estimate(estimate) == is_valid


@pytest.mark.parametrize(
    'estimate_one, estimate_two, conflicts',
    [
        (0, 0, False),
        (1, 1, False),
        (1000, 1000, False),
        (-1000, -1000, False),
        (1000, -1000, True),
        (True, 10, True),
        (10, False, True),
    ]
)
def test_conflicts_with(estimate_one, estimate_two, conflicts, create_bet):
    bet_one = create_bet(estimate_one)
    bet_two = create_bet(estimate_two)

    assert bet_one.conflicts_with(bet_two) == conflicts
