import random as r

from casper.network import Network


def test_new_network(validator_set):
    network = Network(validator_set)
    assert network.validator_set == validator_set
    assert len(network.global_view.messages) == 0


def test_random_initialization(validator_set):
    network = Network(validator_set)

    assert len(network.global_view.messages) == 0
    network.random_initialization()
    assert len(network.global_view.messages) == len(validator_set)


def test_get_message_from_validator(network):
    validator = r.sample(network.validator_set.validators, 1)[0]
    message = network.get_message_from_validator(validator)

    assert message.sender == validator.name


def test_propagate_message_to_validator(network):
    from_validator, to_validator = r.sample(
        network.validator_set.validators,
        2
    )

    message = network.get_message_from_validator(from_validator)
    network.propagate_message_to_validator(message, to_validator)

    assert message in to_validator.view.messages
    assert message == to_validator.view.latest_messages[from_validator.name]
