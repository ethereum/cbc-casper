import pytest

from casper.protocols.order.bet import Bet


@pytest.mark.parametrize(
    'estimate, is_valid',
    [
        ([], True),
        ([(0, 1, 2)], True),
        ([True, False, True], True),
        (-10000000, False),
        (True, False),
        ((0, 1), False),
        (None, False),
    ]
)
def test_accepts_valid_estimates(estimate, is_valid):
    assert Bet.is_valid_estimate(estimate) == is_valid


@pytest.mark.parametrize(
    'estimate_one, estimate_two, conflicts',
    [
        ([1], [1], False),
        ([1, 2, 3], [1, 2, 3], False),
        ([[]], [[]], False),
        (['Hi', 'Hello'], ['Hi', 'Hello'], False),
        ([1], [1, 2], True),
        ([1, 2], [2, 1], True),
        (['Hi', 'Hello'], ['Hi', 'Welcome'], True),
    ]
)
def test_conflicts_with(estimate_one, estimate_two, conflicts, create_bet):
    bet_one = create_bet(estimate_one)
    bet_two = create_bet(estimate_two)

    assert bet_one.conflicts_with(bet_two) == conflicts
