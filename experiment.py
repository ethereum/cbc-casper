import argparse
import json
import os

from numpy import mean

from simulations.experiment import Experiment
from simulations.utils import (
    validator_generator
)


def main():
    parser = argparse.ArgumentParser(description='Run CasperCBC standard simulations.')
    parser.add_argument(
        'json_file', metavar='J', type=str,
        help='specifies the json file with the experiment params'
    )

    args = parser.parse_args()

    with open(args.json_file) as f:
        config = json.load(f)

    experiment = Experiment(
        config['data'],
        config['num_simulations'],
        validator_generator(config['validator_info']),
        config['msg_mode'],
        config['rounds_per_sim'],
        config['report_interval']
    )

    experiment.run()

    if not os.path.exists("out"):
        os.makedirs("out")

    with open("out/{}".format(os.path.basename(args.json_file)), 'w') as f:
        json.dump(experiment.analyzer_data, f, indent=4)

    final_data = experiment.analyzer_data["aggregated"]["final"]
    for data in final_data:
        print("avg {}:\t{}".format(data, mean(final_data[data])))


if __name__ == '__main__':
    main()
