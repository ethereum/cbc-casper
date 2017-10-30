import sys
import pytest

from casper.blockchain.blockchain_protocol import BlockchainProtocol

from casper.network import Network
from simulations.simulation_runner import SimulationRunner
import simulations.utils as utils


@pytest.mark.parametrize(
    'mode, rounds, report_interval',
    [
        ('rand', 10, 2),
        ('rrob', None, None),
    ]
)
def test_new_simulation_runner(validator_set, mode, rounds, report_interval):
    msg_gen = utils.message_maker(mode)
    simulation_runner = SimulationRunner(
        validator_set,
        msg_gen,
        BlockchainProtocol,
        rounds,
        report_interval,
        False,
        False
    )

    assert simulation_runner.validator_set == validator_set
    assert simulation_runner.msg_gen == msg_gen
    assert simulation_runner.round == 0
    assert isinstance(simulation_runner.network, Network)

    if rounds:
        assert simulation_runner.total_rounds == rounds
    else:
        assert simulation_runner.total_rounds == sys.maxsize

    if report_interval:
        assert simulation_runner.report_interval == report_interval
    else:
        assert simulation_runner.report_interval == 1


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


@pytest.mark.parametrize(
    'mode, messages_generated_per_round',
    [
        ('rand', 1),
        ('rrob', 1),
        ('full', 5),
        ('nofinal', 2),
    ]
)
def test_simulation_runner_send_messages(validator_set, mode, messages_generated_per_round):
    msg_gen = utils.message_maker(mode)
    simulation_runner = SimulationRunner(
        validator_set,
        msg_gen,
        BlockchainProtocol,
        100,
        20,
        False,
        False
    )

    assert len(simulation_runner.network.global_view.messages) == len(validator_set)

    for i in range(10):
        simulation_runner.step()
        assert len(simulation_runner.network.global_view.messages) == \
            (i + 1) * messages_generated_per_round + len(validator_set)
