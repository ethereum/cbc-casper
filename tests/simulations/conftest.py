import pytest

import casper.presets as presets
from simulations.simulation_runner import SimulationRunner


@pytest.fixture
def simulation_runner(validator_set):
    msg_gen = presets.message_maker('rand')
    return SimulationRunner(validator_set, msg_gen)
