import random
import pytest

from casper.protocols.integer.integer_protocol import IntegerProtocol
from casper.validator_set import ValidatorSet

from simulations.json_generator import generate_integer_json

@pytest.fixture
def integer_class():
    return IntegerProtocol


@pytest.fixture
def integer_instantiated(integer_class, test_weight):
    return integer_class(
        generate_integer_json(exe_str='', weights=test_weight),
        False,
        False,
        1
    )


@pytest.fixture
def integer_creator(integer_class):
    def creator(weights):
        return integer_class(
            generate_integer_json(exe_str='', weights=weights),
            False,
            False,
            1
        )
    return creator


@pytest.fixture
def integer_validator_set(test_weight, integer_class):
    return ValidatorSet(test_weight, integer_class.View, integer_class.Message)


@pytest.fixture
def create_integer_validator_set(integer_class):
    def create(weight):
        return ValidatorSet(weight, integer_class.View, integer_class.Message)
    return create

@pytest.fixture
def integer_validator(integer_validator_set):
    return random.choice(list(integer_validator_set))


@pytest.fixture
def create_bet(integer_validator):
    def c_bet(estimate):
        return IntegerProtocol.Message(estimate, {}, integer_validator, 0, 0)
    return c_bet
