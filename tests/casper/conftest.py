import pytest

from simulations.json_generator import SELECT_JSON_GENERATOR
from simulations.utils import (
    SELECT_PROTOCOL,
    generate_random_gaussian_weights
)
from simulations.network_delay import (
    no_delay,
    step_delay,
    constant_delay,
    random_delay,
    gaussian_delay
)

PROTOCOL_NAMES = ['binary', 'integer', 'order', 'blockchain', 'concurrent', 'sharding']
DELAY_FUNCTIONS = [no_delay, step_delay, constant_delay, random_delay, gaussian_delay]

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
    temp = protocol_class(protocol_json_gen(exe_str=''), False, False, 1)
    print("Execution should be empty:" + temp.unexecuted)
    return temp


@pytest.fixture(params=DELAY_FUNCTIONS)
def delay_function(request):
    return request.param


@pytest.fixture
def message(protocol_class):
    return protocol_class.Message


@pytest.fixture
def view(protocol_class):
    return protocol_class.View
