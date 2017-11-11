"""The network testing module ... """
import random as r
import pytest

from casper.network import Network


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


@pytest.mark.skip(reason="test not yet implemented")
def test_view_initialization():
    pass
