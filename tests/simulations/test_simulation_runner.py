import sys
import pytest

from casper.network import Network
from simulations.simulation_runner import SimulationRunner
import simulations.utils as utils


@pytest.mark.parametrize(
    'mode, rounds',
    [
        ('rand', 10),
        ('rrob', None),
    ]
)
def test_new_simulation_runner(validator_set, mode, rounds):
    msg_gen = utils.message_maker(mode)
    simulation_runner = SimulationRunner(validator_set, msg_gen, rounds)

    assert simulation_runner.validator_set == validator_set
    assert simulation_runner.msg_gen == msg_gen
    assert simulation_runner.round == 0
    assert isinstance(simulation_runner.network, Network)

    if rounds is None:
        assert simulation_runner.total_rounds == sys.maxsize
    else:
        assert simulation_runner.total_rounds == rounds


@pytest.mark.parametrize(
    'rounds',
    [
        (3),
        (10),
    ]
)
def test_simulation_runner_run(simulation_runner, rounds):
    simulation_runner.total_rounds = rounds
    assert simulation_runner.round == 0

    simulation_runner.run()

    assert simulation_runner.round == rounds


def test_simulation_runner_step(simulation_runner):
    assert simulation_runner.round == 0
    simulation_runner.step()
    assert simulation_runner.round == 1

    for i in range(5):
        simulation_runner.step()

    assert simulation_runner.round == 6
