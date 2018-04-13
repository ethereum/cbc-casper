import random as r
import pytest

from simulations.json_generator import SELECT_JSON_GENERATOR
from simulations.utils import (
    SELECT_PROTOCOL,
    generate_random_gaussian_weights
)

PROTOCOL_NAMES = ['binary', 'integer', 'order', 'blockchain', 'concurrent', 'sharding']


@pytest.fixture(params=PROTOCOL_NAMES)
def protocol_name(request):
    return request.param


@pytest.fixture
def protocol_class(protocol_name):
    return SELECT_PROTOCOL[protocol_name]


@pytest.fixture
def protocol_json_gen(protocol_name):
    return SELECT_JSON_GENERATOR[protocol_name]


@pytest.fixture
def protocol_instantiated(protocol_class, protocol_json_gen):
    return protocol_class(protocol_json_gen())


@pytest.fixture(params=GENESIS_PROTOCOLS)
def genesis_protocol(request):
    return request.param


@pytest.fixture(params=RAND_START_PROTOCOLS)
def rand_start_protocol(request):
    return request.param


@pytest.fixture
def message(protocol):
    return protocol.Message


@pytest.fixture
def example_function():
    def example_func():
        return
    return example_func


@pytest.fixture(autouse=True)
def reset_blockchain_protocol(request):
    BlockchainProtocol.genesis_block = None


@pytest.fixture
def report(request):
    return request.config.getoption("--report")


@pytest.fixture
def empty_just():
    return {}


@pytest.fixture
def test_weight():
    return {i: 5 - i for i in range(5)}


@pytest.fixture
def generate_validator_set():
    return generate_random_gaussian_validator_set


@pytest.fixture
def validator_set(protocol):
    return generate_random_gaussian_validator_set(protocol)


@pytest.fixture
def validator(validator_set):
    return r.choice(list(validator_set.validators))


@pytest.fixture
def to_from_validators(validator_set):
    return r.sample(
        validator_set.validators,
        2
    )


@pytest.fixture
def to_validator(to_from_validators):
    return to_from_validators[0]


@pytest.fixture
def from_validator(to_from_validators):
    return to_from_validators[1]


@pytest.fixture
def network(validator_set, protocol):
    return NoDelayNetwork(validator_set, protocol)


@pytest.fixture
def no_delay_network(validator_set, protocol):
    return NoDelayNetwork(validator_set, protocol)


@pytest.fixture
def constant_delay_network(validator_set, protocol):
    return ConstantDelayNetwork(validator_set, protocol)


@pytest.fixture
def global_view(network):
    return network.global_view
