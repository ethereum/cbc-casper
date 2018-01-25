import random
import pytest

from casper.protocols.concurrent.concurrent_protocol import ConcurrentProtocol


@pytest.fixture
def concurrent_validator_set(generate_validator_set):
    return generate_validator_set(ConcurrentProtocol)


@pytest.fixture
def concurrent_validator(concurrent_validator_set):
    return random.choice(list(concurrent_validator_set))


@pytest.fixture
def empty_concurrent_estimate():
    return {'blocks': {None}, 'inputs': [], 'outputs': []}

@pytest.fixture
def block(empty_just, concurrent_validator, empty_concurrent_estimate):
    return ConcurrentProtocol.Message(empty_concurrent_estimate, empty_just, concurrent_validator, 0, 0)


@pytest.fixture
def create_block(empty_just, concurrent_validator):
    def c_block(estimate):
        return ConcurrentProtocol.Message(estimate, empty_just, concurrent_validator, 0, 0)
    return c_block
