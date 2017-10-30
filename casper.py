'''
Casper PoC: Correct-by-construction asynchronous binary consensus.

Note that comments marked with "#########....#########"" barriers are probably
conceptually important Other comments may be conceptually important but are
mostly for code comprehension Note that not all comments have been marked up in
this manner, yet... :)
'''

import argparse
from configparser import ConfigParser

from simulations.simulation_runner import SimulationRunner
from simulations.utils import (
    generate_random_gaussian_validator_set,
    message_maker,
    protocol_view_class,
    MESSAGE_MODES,
    PROTOCOLS
)

from casper.blockchain.blockchain_view import BlockchainView


def default_configuration():
    config = ConfigParser()
    config.read("config.ini")
    return config["SimulationDefaults"]


def main():
    config = default_configuration()
    parser = argparse.ArgumentParser(description='Run CasperCBC standard simulations.')
    parser.add_argument(
        'mode', metavar='Mode', type=str,
        choices=MESSAGE_MODES,
        help='specifies how to generate and propogate new messages'
    )
    parser.add_argument(
        '--protocol', type=str, default=config.get("DefaultProtocol"),
        choices=PROTOCOLS,
        help='specifies the protocol for the simulation'
    )
    parser.add_argument(
        '--validators', type=int, default=config.getint("NumValidators"),
        help='specifies the number of validators in validator set'
    )
    parser.add_argument(
        '--rounds', type=int, default=config.getint("NumRounds"),
        help='specifies the number of rounds to run the simulation'
    )
    parser.add_argument(
        '--report-interval', type=int, default=config.getint("ReportInterval"),
        help='specifies the interval in rounds at which to plot results'
    )
    parser.add_argument(
        '--hide-display', help='hide simulation display', action='store_true'
    )
    parser.add_argument(
        '--save', help='hide simulation display', action='store_true'
    )

    args = parser.parse_args()

    validator_set = generate_random_gaussian_validator_set(
        protocol_view_class(args.protocol),
        args.validators
    )
    msg_gen = message_maker(args.mode)
    display = not args.hide_display

    simulation_runner = SimulationRunner(
        validator_set,
        msg_gen,
        protocol_view_class(args.protocol),
        total_rounds=args.rounds,
        report_interval=args.report_interval,
        display=display,
        save=args.save,
    )
    simulation_runner.run()


if __name__ == "__main__":
    main()
