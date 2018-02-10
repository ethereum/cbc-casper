import pytest

from simulations.message_modes import RandomMessageMode

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from simulations.simulation_runner import SimulationRunner
import simulations.utils as utils


@pytest.fixture
def simulation_runner(protocol, validator_set, network):
    message_mode = RandomMessageMode()
    return SimulationRunner(
        validator_set,
        message_mode,
        protocol,
        network,
        20,
        20,
        False,
        False
    )
