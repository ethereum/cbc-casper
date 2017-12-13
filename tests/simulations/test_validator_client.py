"""ValidatorClient testing module ... """
import pytest
from casper.message import Message
from simulations.validator_client import ValidatorClient


#
# Helpers
#
def true():
    return True


def false():
    return False


#
# Tests
#
def test_new_validator_client(validator, network):
    client = ValidatorClient(validator, network)
    assert client.validator == validator
    assert client.network == network


def test_make_new_message_if_should(validator_client):
    validator_client.should_make_new_message = true
    message = validator_client.make_new_message()

    assert message
    assert message.hash in validator_client.validator.view.justified_messages


def test_make_new_message_if_should_not(validator_client):
    validator_client.should_make_new_message = false
    message = validator_client.make_new_message()

    assert message is None


def test_validator_client_time(validator_client):
    assert validator_client.time == 0
    validator_client.advance_time()
    assert validator_client.time == 1
    validator_client.set_time(100)
    assert validator_client.time == 100


@pytest.mark.parametrize(
    'num_messages',
    [
        (1),
        (5)
    ]
)
def test_retrieve_messages(no_delay_network, to_validator, from_validator, num_messages):
    validator_client = ValidatorClient(to_validator, no_delay_network)
    sent_messages = []
    for i in range(num_messages):
        message = from_validator.make_new_message()
        no_delay_network.send(validator_client.validator, message)
        sent_messages.append(message)

    received_messages = validator_client.retrieve_messages()
    assert set(received_messages) == set(sent_messages)
    for message in sent_messages:
        assert message.hash in validator_client.validator.view.justified_messages


def test_propagate_message(network, validator_client):
    validator_client.should_make_new_message = true
    message = validator_client.make_new_message()
    assert message

    validator_client.propagate_message(message)
    assert network.message_queues[validator_client.validator].qsize() == 0
    for validator in network.validator_set:
        if validator == validator_client.validator:
            continue
        message_queue = network.message_queues[validator]
        assert message_queue.qsize() == 1
        assert message_queue.peek()[1] == message


def test_make_and_propagate_message_when_should(network, global_view, validator_client):
    validator_client.should_make_new_message = true
    message = validator_client.make_and_propagate_message()
    assert message
    assert message.hash in global_view.justified_messages


def test_make_and_propagate_message_when_should_not(network, global_view, validator_client):
    validator_client.should_make_new_message = false
    global_justified_messages_length = len(global_view.justified_messages)

    message = validator_client.make_and_propagate_message()
    assert not message
    assert len(global_view.justified_messages) == global_justified_messages_length


def test_is_thread(validator_client):
    assert validator_client.start
