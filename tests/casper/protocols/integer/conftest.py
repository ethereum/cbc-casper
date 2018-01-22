import random
import pytest

from casper.protocols.integer.integer_protocol import IntegerProtocol


@pytest.fixture
def integer_validator(generate_validator_set):
    return random.choice(list(generate_validator_set(IntegerProtocol)))


@pytest.fixture
def bet(empty_just, integer_validator):
    return IntegerProtocol.Message(0, empty_just, integer_validator, 0, 0)


@pytest.fixture
def create_bet(empty_just, integer_validator):
    def c_bet(estimate):
        return IntegerProtocol.Message(estimate, empty_just, integer_validator, 0, 0)
    return c_bet
