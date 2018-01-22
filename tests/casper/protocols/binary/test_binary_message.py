import random as r
import pytest

from casper.protocols.binary.bet import Bet
from casper.protocols.binary.binary_protocol import BinaryProtocol

@pytest.mark.parametrize(
    'estimate, is_valid',
    [
        (0, True),
        (1, True),
        (True, True),
        (False, True),
        (-1, False),
        (2, False),
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
        (False, 0, False),
        (True, 1, False),
        (1, 0, True),
        (0, 1, True),
        (True, 0, True),
        (1, False, True),
    ]
)
def test_conflicts_with(estimate_one, estimate_two, conflicts, create_bet):
    bet_one = create_bet(estimate_one)
    bet_two = create_bet(estimate_two)

    assert bet_one.conflicts_with(bet_two) == conflicts
