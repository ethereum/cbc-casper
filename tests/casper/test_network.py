"""The network testing module ... """
import random as r
import pytest

from casper.network import Network
from simulations.testing_language import TestLangCBC


def test_new_network(validator_set):
    network = Network(validator_set)
    assert network.validator_set == validator_set
    assert not any(network.global_view.justified_messages)


def test_random_initialization(validator_set):
    network = Network(validator_set)

    assert not any(network.global_view.justified_messages)
    network.random_initialization()
    assert len(network.global_view.justified_messages) == len(validator_set)


def test_get_message_from_validator(network):
    validator = r.sample(network.validator_set.validators, 1)[0]
    message = network.get_message_from_validator(validator)

    assert message.sender == validator


def test_propagate_message_to_validator(network):
    from_validator, to_validator = r.sample(
        network.validator_set.validators,
        2
    )

    message = network.get_message_from_validator(from_validator)
    network.propagate_message_to_validator(message, to_validator)

    assert message in to_validator.view.pending_messages.values()


@pytest.mark.parametrize(
    'test_string, num_messages',
    [
        ('RR0-A RR0-B', 9),
        ('B0-A S1-A B1-B S2-B', 5),
        ('B0-A S1-A RR1-B', 7),
    ]
)
def test_view_initialization(test_string, num_messages, validator_set):
    test_lang = TestLangCBC({0: 5, 1: 6, 2: 7})
    test_lang.parse(test_string)

    global_view = test_lang.network.global_view

    assert len(global_view.justified_messages) == num_messages

    network = Network(validator_set)
    network.view_initialization(test_lang.network.global_view)

    for validator in validator_set:
        view = validator.view
        total_messages = len(view.justified_messages) + len(view.pending_messages)
        assert total_messages == num_messages
