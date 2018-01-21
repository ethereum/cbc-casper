import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from simulations.simulation_runner import SimulationRunner
import simulations.utils as utils


@pytest.fixture
def simulation_runner(protocol, validator_set, network):
    msg_gen = utils.message_maker('rand')
    return SimulationRunner(
        validator_set,
        msg_gen,
        protocol,
        network,
        20,
        20,
        False,
        False
    )
