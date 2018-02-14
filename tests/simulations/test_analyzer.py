import pytest

from simulations.message_modes import (
    RandomMessageMode,
    RoundRobinMessageMode,
    FullMessageMode,
    NoFinalMessageMode,
)

from casper.networks import NoDelayNetwork
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol

from simulations.analyzer import Analyzer
from simulations.simulation_runner import SimulationRunner
import simulations.utils as utils


@pytest.mark.parametrize(
    'message_mode, messages_generated_per_round',
    [
        (RandomMessageMode, 1),
        (RoundRobinMessageMode, 1),
        (FullMessageMode, 5),
        (NoFinalMessageMode, 2),
    ]
)
def test_num_messages_genesis(generate_validator_set, genesis_protocol, message_mode, messages_generated_per_round):
    validator_set = generate_validator_set(genesis_protocol)
    network = NoDelayNetwork(validator_set, genesis_protocol)
    msg_gen = message_mode()
    simulation_runner = SimulationRunner(
        validator_set,
        msg_gen,
        BlockchainProtocol,
        network,
        100,
        20,
        False,
        False
    )
    analyzer = Analyzer(simulation_runner)

    assert analyzer.num_messages == 1
    potential_extra_messages = len(validator_set) - 1

    for i in range(10):
        simulation_runner.step()
        messages_generated = 1 + (i + 1) * messages_generated_per_round

        assert analyzer.num_messages <= messages_generated + potential_extra_messages


@pytest.mark.skip(reason="test not written")
def test_num_safe_messages():
    pass


@pytest.mark.skip(reason="test not written")
@pytest.mark.parametrize(
    'num_blocks, num_blocks_at_or_below_safe_tip, safe_tip_number, expected',
    [
        (5, 5, 2, 0.40),
        (2, 2, 0, 0.50),
        (2, 0, -1, 0.0),
        (10, 8, 4, 0.375),
        (20, 10, 9, 0.0),
    ]
)
def test_orphan_rate(
        simulation_runner,
        mock_block,
        num_blocks,
        num_blocks_at_or_below_safe_tip,
        safe_tip_number,
        expected
        ):
    pass
