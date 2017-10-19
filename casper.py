'''
Casper PoC: Correct-by-construction asynchronous binary consensus.

Note that comments marked with "#########....#########"" barriers are probably
conceptually important Other comments may be conceptually important but are
mostly for code comprehension Note that not all comments have been marked up in
this manner, yet... :)
'''

import argparse

import casper.presets as presets
from casper.simulation_utils import (
    generate_random_validator_set
)
from simulations.simulation_runner import SimulationRunner


def main():
    parser = argparse.ArgumentParser(description='Run CasperCBC standard simulations.')
    parser.add_argument(
        'mode', metavar='Mode', type=str,
        choices=presets.MESSAGE_MODES,
        help='specifies how to generate and propogate new messages'
    )
    parser.add_argument(
        '--validators', type=int, default=5,
        help='specifies the number of validators in validator set'
    )
    parser.add_argument(
        '--rounds', type=int, default=100,
        help='specifies the number of rounds to run the simulation'
    )
    parser.add_argument(
        '--report-interval', type=int, default=20,
        help='specifies the interval in rounds at which to plot results'
    )

    args = parser.parse_args()

    validator_set = generate_random_validator_set(args.validators)
    msg_gen = presets.message_maker(args.mode)

    simulation_runner = SimulationRunner(
        validator_set,
        msg_gen,
        total_rounds=args.rounds,
        report_interval=args.report_interval,
        report=True
    )
    simulation_runner.run()


if __name__ == "__main__":
    main()
