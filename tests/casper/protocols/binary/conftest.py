import random
import pytest

from casper.protocols.binary.binary_protocol import BinaryProtocol

@pytest.fixture
def binary_validator_set(generate_validator_set):
    return generate_validator_set(BinaryProtocol)


@pytest.fixture
def binary_validator(binary_validator_set):
    return random.choice(list(binary_validator_set))


@pytest.fixture
def bet(empty_just, binary_validator):
    return BinaryProtocol.Message(0, empty_just, binary_validator, 0, 0)

@pytest.fixture
def create_bet(empty_just, binary_validator):
    def c_bet(estimate):
        return BinaryProtocol.Message(estimate, empty_just, binary_validator, 0, 0)
    return c_bet
