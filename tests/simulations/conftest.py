from collections import namedtuple

import pytest

from simulations.simulation_runner import SimulationRunner
import simulations.utils as utils


@pytest.fixture
def simulation_runner(validator_set):
    msg_gen = utils.message_maker('rand')
    return SimulationRunner(validator_set, msg_gen, 20)


@pytest.fixture
def mock_block():
    return namedtuple("Block", ["sequence_number", "id"])
