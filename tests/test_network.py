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
