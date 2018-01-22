import random
import pytest

from casper.protocols.order.order_protocol import OrderProtocol

@pytest.fixture
def order_validator_set(generate_validator_set):
    return generate_validator_set(OrderProtocol)


@pytest.fixture
def order_validator(order_validator_set):
    return random.choice(list(order_validator_set))


@pytest.fixture
def bet(empty_just, order_validator):
    return OrderProtocol.Message([0, 1], empty_just, order_validator, 0, 0)


@pytest.fixture
def create_bet(empty_just, order_validator):
    def c_bet(estimate):
        return OrderProtocol.Message(estimate, empty_just, order_validator, 0, 0)
    return c_bet
