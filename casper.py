'''
Correct-by-construction Casper PoC

Asynchronous consensus on a variety of data structures, including:
a bit, an integer, a list, a blockchain, a concurrent schedule,
and a sharded blockchain.

For more information,
join the gitter: https://gitter.im/cbc-casper/Lobby
read the wiki:

'''
import pprint
import argparse
from configparser import ConfigParser

from simulations.utils import (
    str2bool,
    exestr,
    SELECT_PROTOCOL,

)
from simulations.json_generator import SELECT_JSON_GENERATOR

NOT_NEEDED = {'protocol', 'display', 'save', 'report_interval'}

def default_configuration():
    """Returns default configuration for execution"""
    config = ConfigParser()
    config.read("config.ini")
    return config["SimulationDefaults"]


def main():
    """Generates and runs specified CBC Casper simulation"""
    config = default_configuration()
    parser = argparse.ArgumentParser(description='Run CasperCBC standard simulations.')
    parser.add_argument(
        '--protocol', type=str, default=config.get("Protocol"),
        choices=SELECT_PROTOCOL.keys(),
        help='specifies which data structure to form consensus on'
    )
    parser.add_argument(
        '--validators', type=int, default=config.getint("Validators"),
        help='specifies the number of validators'
    )
    parser.add_argument(
        '--weights', nargs='+', type=int, default=None,
        help='specifies the weights of the validators'
    )
    parser.add_argument(
        '--exe-str', type=exestr, default=None,
        help='specifies a specific execution (message creation and delivery)'
    )
    parser.add_argument(
        '--msg-mode', type=str, default=config.get("MsgMode"),
        help='specifies message passing schemes of the validators'
    )
    parser.add_argument(
        '--network', type=str, default=config.get("Network"),
        help='specifies network conditions for message passing'
    )
    parser.add_argument(
        '--rounds', type=int, default=config.getint("Rounds"),
        help='specifies the number of rounds to run the simulation'
    )
    parser.add_argument(
        '--report-interval', type=int, default=config.getint("ReportInterval"),
        help='specifies the interval (in rounds) at which to plot results'
    )
    parser.add_argument(
        '--display', type=str2bool, default=config.getboolean("Display"),
        help='show the view graphs as they are created'
    )
    parser.add_argument(
        '--save', type=str2bool, default=config.getboolean("Save"),
        help='save the viewgraphs in graphs/ directory'
    )

    args = parser.parse_args()
    generate_json = SELECT_JSON_GENERATOR[args.protocol]

    # not all parameters are needed to generate the json for execution
    execution_string = generate_json(**{k: v for k, v in vars(args).items() if k not in NOT_NEEDED})
    print(type(execution_string))

    protocol = SELECT_PROTOCOL[args.protocol](
        execution_string,
        args.display,
        args.save,
        args.report_interval
    )

    protocol.execute()


if __name__ == "__main__":
    main()
