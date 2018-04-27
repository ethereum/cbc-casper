import pytest

from simulations.json_generator import SELECT_JSON_GENERATOR
from simulations.utils import (
    SELECT_PROTOCOL,
    generate_random_gaussian_weights
)

from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.safety_oracles.turan_oracle import TuranOracle
from casper.safety_oracles.adversary_oracle import AdversaryOracle

ORACLES = [CliqueOracle, TuranOracle, AdversaryOracle]
SAFETY_ORACLE_PROTOCOL_NAMES = ['binary', 'integer', 'blockchain']


@pytest.fixture(params=ORACLES)
def oracle_class(request):
    return request.param


@pytest.fixture(params=SAFETY_ORACLE_PROTOCOL_NAMES)
def so_protocol_name(request):
    return request.param


@pytest.fixture
def so_protocol_instantiated(so_protocol_name, test_weight):
    return SELECT_PROTOCOL[so_protocol_name](
        SELECT_JSON_GENERATOR[so_protocol_name](exe_str='', weights=test_weight),
        False,
        False,
        1
    )


@pytest.fixture
def so_protocol_creator(so_protocol_name):
    def create_with_weights(weights):
        return SELECT_PROTOCOL[so_protocol_name](
            SELECT_JSON_GENERATOR[so_protocol_name](exe_str='', validators=len(weights), weights=weights),
            False,
            False,
            1
        )
    return create_with_weights
