import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from simulations.networks.simple_networks import (
    ConstantDelayNetwork,
    NoDelayNetwork
)
from simulations.simulation_runner import SimulationRunner
from simulations.validator_client import ValidatorClient

import simulations.utils as utils


@pytest.fixture
def simulation_runner(validator_set, network):
    msg_strategy = utils.message_strategy('rand')
    return SimulationRunner(
        validator_set,
        msg_strategy,
        BlockchainProtocol,
        network,
        20,
        20,
        False,
        False
    )


#
# Network Fixtures
#

@pytest.fixture
def network(validator_set):
    return NoDelayNetwork(validator_set)


@pytest.fixture
def no_delay_network(validator_set):
    return NoDelayNetwork(validator_set)


@pytest.fixture
def constant_delay_network(validator_set):
    return ConstantDelayNetwork(validator_set)


@pytest.fixture
def global_view(network):
    return network.global_view


#
# Validator Client Fixtures
#

@pytest.fixture
def validator_client(validator, network):
    return ValidatorClient(validator, network)
