import pytest

from simulations.analyzer import Analyzer
from simulations.simulation_runner import SimulationRunner
import simulations.utils as utils


@pytest.mark.parametrize(
    'mode, messages_generated_per_round',
    [
        ('rand', 1),
        ('rrob', 1),
        ('full', 5),
        ('nofinal', 2),
    ]
)
def test_num_messages(validator_set, mode, messages_generated_per_round):
    msg_gen = utils.message_maker(mode)
    simulation_runner = SimulationRunner(validator_set, msg_gen, 100, 20, False, False)
    analyzer = Analyzer(simulation_runner)

    # due to random_initialization
    assert analyzer.num_messages() == len(validator_set)

    for i in range(10):
        simulation_runner.step()
        assert analyzer.num_messages() == \
            len(validator_set) + (i + 1) * messages_generated_per_round


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
