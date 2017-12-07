import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.validator_set import ValidatorSet
from simulations.utils import (
    generate_random_gaussian_validator_set,
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
def test_generate_random_gaussian_validator_set(
        num_validators,
        mu,
        sigma,
        min_weight
        ):
    vs = generate_random_gaussian_validator_set(
        BlockchainProtocol,
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
        message_makers = msg_gen(validator_set)
        assert len(message_makers) == 1
        for validator in message_makers:
            assert validator in validator_set


def test_round_robin_message_maker(validator_set):
    msg_gen = message_maker("rrob")

    assert msg_gen.next_sender_index == 0
    senders = validator_set.sorted_by_name()
    # receivers = senders[1:] + senders[0:1]

    for i in range(3):
        for j in range(len(validator_set)):
            message_makers = msg_gen(validator_set)
            assert len(message_makers) == 1
            validator = message_makers[0]
            assert validator == senders[j]


@pytest.mark.parametrize(
    'weights',
    [
        (
            {"jim": 1, "dan": 30}
        ),
        (
            {0: 10, 1: 8, 2: 12}
        ),
    ]
)
def test_full_message_maker(weights):
    print(weights)
    validator_set = ValidatorSet(weights)
    msg_gen = message_maker("full")

    message_makers = msg_gen(validator_set)
    assert len(validator_set) == len(message_makers)
    assert set(validator_set.validators) == set(message_makers)


def test_no_final_message_maker(validator_set):
    msg_gen = message_maker("nofinal")

    senders = validator_set.sorted_by_name()

    for i in range(3):
        for j in range(len(validator_set)):
            index = j * 2 % len(validator_set)
            message_paths = msg_gen(validator_set)
            assert len(message_paths) == 2

            # first rr message this round
            first_validator = message_paths[0]
            assert first_validator == senders[index]

            # second rr message this round
            second_validator = message_paths[1]
            assert second_validator == senders[(index + 1) % len(validator_set)]
