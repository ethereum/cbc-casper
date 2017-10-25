import argparse
import random

from numpy import mean

from casper.validator_set import ValidatorSet
from simulations.experiment import Experiment
from simulations.utils import (
    MESSAGE_MODES
)


def constant_validator_set_generator(weights):
    # ensure no ties
    jitter_weights = {
        name: weights[name] + random.random()
        for name in weights
    }

    def generator():
        return ValidatorSet(jitter_weights)

    return generator


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
    report_interval = 20

    validator_weights = {0: 15, 1: 18, 2: 21, 3: 24, 4: 27}

    data = [
        "orphan_rate",
        "num_messages",
        "num_safe_messages"
    ]

    experiment = Experiment(
        data,
        num_simulations,
        constant_validator_set_generator(validator_weights),
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
