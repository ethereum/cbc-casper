import argparse

from numpy import mean

from simulations.analyzer import Analyzer
from simulations.simulation_runner import SimulationRunner
from simulations.utils import (
    generate_random_validator_set,
    message_maker,
    MESSAGE_MODES
)


def main():
    parser = argparse.ArgumentParser(description='Run CasperCBC standard simulations.')
    parser.add_argument(
        'mode', metavar='Mode', type=str,
        choices=MESSAGE_MODES,
        help='specifies which message generation/propogation scheme to use'
    )

    args = parser.parse_args()

    num_simulations = 20
    rounds_per_sim = 100
    num_validators = 5
    mu = 100
    sigma = 20
    min_weight = 20

    analyzer_data = {
        "orphan_rate": [],
        "num_messages": [],
        "num_safe_messages": []
    }

    print("Running", end='')
    for i in range(num_simulations):
        validator_set = generate_random_validator_set(
            num_validators,
            mu,
            sigma,
            min_weight
        )
        runner = SimulationRunner(
            validator_set,
            message_maker(args.mode),
            total_rounds=rounds_per_sim,
        )
        runner.run()
        analyzer = Analyzer(runner)
        for method in analyzer_data:
            analyzer_data[method].append(getattr(analyzer, method)())

        print(".", end='', flush=True)

    print(" complete!")

    orphan_rates = analyzer_data["orphan_rate"]
    num_messages = analyzer_data["num_messages"]
    num_safe_messages = analyzer_data["num_safe_messages"]

    print("min orphan rate:\t{}".format(min(orphan_rates)))
    print("max orphan rate:\t{}".format(max(orphan_rates)))
    print("avg orphan_rate:\t{}".format(mean(orphan_rates)))
    print("total blocks:\t\t{}".format(int(mean(num_messages))))
    print("avg safe blocks:\t{}".format(mean(num_safe_messages)))


if __name__ == '__main__':
    main()
