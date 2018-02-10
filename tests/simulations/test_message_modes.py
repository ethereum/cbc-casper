import pytest

from simulations.message_modes import (
    RandomMessageMode,
    RoundRobinMessageMode,
    FullMessageMode,
    NoFinalMessageMode,
)


def test_random_message_maker(validator_set):
    message_mode = RandomMessageMode()

    for i in range(20):
        message_makers = message_mode.get_message_makers(validator_set)
        assert len(message_makers) == 1
        for validator in message_makers:
            assert validator in validator_set


def test_round_robin_message_maker(validator_set):
    message_mode = RoundRobinMessageMode()

    last_maker_name = 0
    for i in range(20):
        message_makers = message_mode.get_message_makers(validator_set)
        assert len(message_makers) == 1
        assert (last_maker_name + 1) % len(validator_set) == message_makers[0].name
        last_maker_name = (last_maker_name + 1) % len(validator_set)


def test_full_message_maker(validator_set):
    message_mode = FullMessageMode()

    message_makers = message_mode.get_message_makers(validator_set)
    assert len(validator_set) == len(message_makers)
    assert set(validator_set.validators) == set(message_makers)


def test_no_final_message_maker(validator_set):
    pass
