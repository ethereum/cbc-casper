import argparse

from numpy import mean

from simulations.experiment import Experiment
from simulations.utils import (
    generate_random_validator_set,
    MESSAGE_MODES
)


def validator_set_generator():
    num_validators = 5
    mu = 100
    sigma = 20
    min_weight = 20

    return generate_random_validator_set(
        num_validators,
        mu,
        sigma,
        min_weight
    )


def main():
    parser = argparse.ArgumentParser(description='Run CasperCBC standard simulations.')
    parser.add_argument(
        'mode', metavar='Mode', type=str,
        choices=MESSAGE_MODES,
        help='specifies which message generation/propogation scheme to use'
    )

    args = parser.parse_args()

    num_simulations = 5
    rounds_per_sim = 100
    report_interval = 20

    data = [
        "orphan_rate",
        "num_messages",
        "num_safe_messages"
    ]

    experiment = Experiment(
        data,
        num_simulations,
        validator_set_generator,
        args.mode,
        rounds_per_sim,
        report_interval
    )

    experiment.run()

    final_data = experiment.final_data
    print("min orphan rate:\t{}".format(min(final_data["orphan_rate"])))
    print("max orphan rate:\t{}".format(max(final_data["orphan_rate"])))
    print("avg orphan_rate:\t{}".format(mean(final_data["orphan_rate"])))
    print("total blocks:\t\t{}".format(int(mean(final_data["num_messages"]))))
    print("avg safe blocks:\t{}".format(mean(final_data["num_safe_messages"])))


if __name__ == '__main__':
    main()
