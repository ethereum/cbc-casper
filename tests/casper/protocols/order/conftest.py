import random
import pytest

from casper.protocols.order.order_protocol import OrderProtocol
from casper.validator_set import ValidatorSet

from simulations.json_generator import generate_order_json

@pytest.fixture
def order_class():
    return OrderProtocol


@pytest.fixture
def order_instantiated(order_class, test_weight):
    return order_class(
        generate_order_json(exe_str='', weights=test_weight),
        False,
        False,
        1
    )


@pytest.fixture
def order_creator(order_class):
    def creator(weights):
        return order_class(
            generate_order_json(exe_str='', weights=weights),
            False,
            False,
            1
        )
    return creator


@pytest.fixture
def order_validator_set(test_weight, order_class):
    return ValidatorSet(test_weight, order_class.View, order_class.Message)


@pytest.fixture
def create_order_validator_set(order_class):
    def create(weight):
        return ValidatorSet(weight, order_class.View, order_class.Message)
    return create


@pytest.fixture
def order_validator(order_validator_set):
    return random.choice(list(order_validator_set))


@pytest.fixture
def create_bet(order_validator):
    def c_bet(estimate):
        return OrderProtocol.Message(estimate, {}, order_validator, 0, 0)
    return c_bet
