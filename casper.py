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
    SELECT_NETWORK,
    SELECT_PROTOCOL,
    SELECT_MESSAGE_MODE,
)


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def default_configuration():
    config = ConfigParser()
    config.read("config.ini")
    return config["SimulationDefaults"]


def main():
    config = default_configuration()
    parser = argparse.ArgumentParser(description='Run CasperCBC standard simulations.')
    parser.add_argument(
        'mode', metavar='Mode', type=str,
        choices=SELECT_MESSAGE_MODE.keys(),
        help='specifies how to generate and propogate new messages'
    )
    parser.add_argument(
        '--protocol', type=str, default=config.get("DefaultProtocol"),
        choices=SELECT_PROTOCOL.keys(),
        help='specifies the protocol for the simulation'
    )
    parser.add_argument(
        '--network', type=str, default=config.get("DefaultNetwork"),
        choices=SELECT_NETWORK.keys(),
        help='specifies the network model for the simulation'
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
        '--hide-display', action="store_true",
        help='display simulations round by round'
    )
    parser.add_argument(
        '--save', type=str2bool, default=config.getboolean("Save"),
        help='save the simulation in graphs/ directory'
    )
    parser.add_argument(
        '--justify-messages', type=str2bool, default=config.getboolean("JustifyMessages"),
        help='force full propagation of all messages in justification of message when sending'
    )

    args = parser.parse_args()
    protocol = SELECT_PROTOCOL[args.protocol]
    network_type = SELECT_NETWORK[args.network]

    validator_set = generate_random_gaussian_validator_set(
        protocol,
        args.validators
    )
    network = network_type(validator_set, protocol)

    message_mode = SELECT_MESSAGE_MODE[args.mode]()

    simulation_runner = SimulationRunner(
        validator_set,
        message_mode,
        protocol=protocol,
        network=network,
        total_rounds=args.rounds,
        report_interval=args.report_interval,
        display=(not args.hide_display),
        save=args.save,
    )
    simulation_runner.run()


if __name__ == "__main__":
    main()
