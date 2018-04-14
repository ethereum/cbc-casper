import pytest

import simulations.network_delay as network
from simulations.json_generator import SELECT_JSON_GENERATOR
from simulations.utils import (
    SELECT_PROTOCOL,
    generate_random_gaussian_weights
)

PROTOCOL_NAMES = ['binary', 'integer', 'order', 'blockchain', 'concurrent', 'sharding']


@pytest.fixture
def test_weight():
    # these are random, decreasing weights
    return [10.123, 9.8293, 8.8873, 7.5564, 6.1245562]


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
def protocol_instantiated(protocol_class, protocol_json_gen, test_weight):
    return protocol_class(
        protocol_json_gen(exe_str='', weights=test_weight),
        False,
        False,
        1
    )


@pytest.fixture
def message(protocol_class):
    return protocol_class.Message


@pytest.fixture
def view(protocol_class):
    return protocol_class.View


@pytest.fixture
def no_delay():
    return network.no_delay
