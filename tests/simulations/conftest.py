import pytest

from casper.blockchain.blockchain_view import BlockchainView
from simulations.simulation_runner import SimulationRunner
import simulations.utils as utils


@pytest.fixture
def simulation_runner(validator_set):
    msg_gen = utils.message_maker('rand')
    return SimulationRunner(validator_set, msg_gen, BlockchainView, 20, 20, False, False)
