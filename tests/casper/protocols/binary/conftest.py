import random
import pytest

from casper.validator_set import ValidatorSet
from casper.protocols.binary.binary_protocol import BinaryProtocol
from simulations.json_generator import generate_binary_json


@pytest.fixture
def binary_class():
    return BinaryProtocol


@pytest.fixture
def binary_instantiated(binary_class, test_weight):
    return binary_class(
        generate_binary_json(exe_str='', weights=test_weight),
        False,
        False,
        1
    )


@pytest.fixture
def binary_creator(binary_class):
    def creator(weights):
        return binary_class(
            generate_binary_json(exe_str='', weights=weights),
            False,
            False,
            1
        )
    return creator


@pytest.fixture
def binary_validator_set(test_weight, binary_class):
    return ValidatorSet(test_weight, binary_class.View, binary_class.Message)


@pytest.fixture
def create_binary_validator_set(binary_class):
    def create(weights):
        return ValidatorSet(weights, binary_class.View, binary_class.Message)
    return create


@pytest.fixture
def binary_validator(binary_validator_set):
    return random.choice(list(binary_validator_set))


@pytest.fixture
def create_bet(binary_validator):
    def c_bet(estimate):
        return BinaryProtocol.Message(estimate, {}, binary_validator, 0, 0)
    return c_bet
