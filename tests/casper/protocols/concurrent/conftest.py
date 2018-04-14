import random
import pytest

from casper.protocols.concurrent.concurrent_protocol import ConcurrentProtocol
from casper.validator_set import ValidatorSet

from simulations.json_generator import generate_concurrent_json

@pytest.fixture
def concurrent_class():
    return ConcurrentProtocol


@pytest.fixture
def concurrent_instantiated(concurrent_class, test_weight):
    return concurrent_class(
        generate_concurrent_json(exe_str='', weights=test_weight),
        False,
        False,
        1
    )


@pytest.fixture
def concurrent_creator(concurrent_class):
    def creator(weights):
        return concurrent_class(
            generate_concurrent_json(exe_str='', weights=weights),
            False,
            False,
            1
        )
    return creator


@pytest.fixture
def concurrent_validator_set(test_weight, concurrent_class):
    return ValidatorSet(test_weight, concurrent_class.View, concurrent_class.Message)


@pytest.fixture
def concurrent_validator(concurrent_validator_set):
    return random.choice(list(concurrent_validator_set))


@pytest.fixture
def create_block(concurrent_validator):
    def c_block(estimate):
        return ConcurrentProtocol.Message(estimate, {}, concurrent_validator, 0, 0)
    return c_block
