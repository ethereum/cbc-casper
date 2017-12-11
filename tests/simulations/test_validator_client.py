"""ValidatorClient testing module ... """
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
def test_new_validator_client(validator):
    client = ValidatorClient(validator)
    assert client.validator == validator


def test_make_new_message_if_should(validator_client):
    validator_client.should_make_new_message = true
    message = validator_client.make_new_message()

    assert message
    assert message.hash in validator_client.validator.view.justified_messages


def test_make_new_message_if_should_net(validator_client):
    validator_client.should_make_new_message = false
    message = validator_client.make_new_message()

    assert message is None
