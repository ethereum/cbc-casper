import pytest

from simulations.simulation_runner import SimulationRunner
import simulations.utils as utils


@pytest.fixture
def simulation_runner(validator_set):
    msg_gen = utils.message_maker('rand')
    return SimulationRunner(validator_set, msg_gen)
