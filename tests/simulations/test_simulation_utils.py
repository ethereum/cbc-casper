import pytest

from casper.validator_set import ValidatorSet
from simulations.utils import (
    generate_random_validator_set,
    message_maker
)


@pytest.mark.parametrize(
    'num_validators, mu, sigma, min_weight',
    [
        (5, 60, 40, 20),
        (2, 50, 20, 10),
        (40, 50, 50, 10),
        (40, 50, 0, 10),
    ]
)
def test_generate_random_validator_set(
        num_validators,
        mu,
        sigma,
        min_weight
        ):
    vs = generate_random_validator_set(
        num_validators,
        mu,
        sigma,
        min_weight
    )

    assert len(vs.validators) == num_validators
    assert min(vs.validator_weights()) >= min_weight
    assert len(set(vs.validator_weights())) == num_validators, "Weights should be unique."



def test_random_message_maker(validator_set):
    msg_gen = message_maker("rand")

    for i in range(20):
        message_paths = msg_gen(validator_set)
        assert len(message_paths) == 1
        for message_path in message_paths:
            assert len(message_path) == 2
            for validator in message_path:
                assert validator in validator_set


def test_round_robin_message_maker(validator_set):
    msg_gen = message_maker("rrob")

    assert msg_gen.next_sender_index == 0
    senders = validator_set.sorted_by_name()
    receivers = senders[1:] + senders[0:1]

    for i in range(3):
        for j in range(len(validator_set)):
            message_paths = msg_gen(validator_set)
            assert len(message_paths) == 1
            message_path = message_paths[0]
            assert len(message_path) == 2
            assert message_path[0] == senders[j]
            assert message_path[1] == receivers[j]


@pytest.mark.parametrize(
    'weights, pairs',
    [
        (
            {"jim": 1, "dan": 30},
            [["jim", "dan"], ["dan", "jim"]]
        ),
        (
            {0: 10, 1: 8, 2: 12},
            [
                [0, 1], [0, 2], [1, 2],
                [1, 0], [2, 0], [2, 1]
            ]
        ),
    ]
)
def test_full_message_maker(weights, pairs):
    validator_set = ValidatorSet(weights)
    msg_gen = message_maker("full")

    message_paths = msg_gen(validator_set)
    for sender_name, receiver_name in pairs:
        sender = validator_set.get_validator_by_name(sender_name)
        receiver = validator_set.get_validator_by_name(receiver_name)
        assert (sender, receiver) in message_paths


def test_no_final_message_maker(validator_set):
    msg_gen = message_maker("nofinal")

    senders = validator_set.sorted_by_name()
    receivers = senders[1:] + senders[0:1]

    for i in range(3):
        for j in range(len(validator_set)):
            index = j * 2 % len(validator_set)
            message_paths = msg_gen(validator_set)
            assert len(message_paths) == 2

            # first rr message this round
            first_message_path = message_paths[0]
            assert len(first_message_path) == 2
            assert first_message_path[0] == senders[index]
            assert first_message_path[1] == receivers[index]

            # second rr message this round
            second_message_path = message_paths[1]
            assert len(second_message_path) == 2
            assert second_message_path[0] == senders[(index + 1) % len(validator_set)]
            assert second_message_path[1] == receivers[(index + 1) % len(validator_set)]
