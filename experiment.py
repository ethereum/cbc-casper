import argparse
import csv
import json
import os

from statistics import mean, stdev

from simulations.experiment import Experiment
from simulations.utils import (
    validator_generator
)


def create_output_dir():
    if not os.path.exists("out"):
        os.makedirs("out")


def write_to_json(experiment, file_path):
    create_output_dir()
    with open("out/{}".format(os.path.basename(file_path)), 'w') as f:
        json.dump(experiment.analyzer_data, f, indent=4)


def write_to_csv(experiment, file_path):
    create_output_dir()
    base_name = os.path.basename(file_path)
    file_name = os.path.splitext(base_name)[0]
    with open("out/{}.csv".format(file_name), 'w') as csvfile:
        aggregated_data = experiment.analyzer_data["aggregated"]
        writer = csv.DictWriter(csvfile, fieldnames=aggregated_data[0].keys())

        writer.writeheader()
        for interval in aggregated_data:
            writer.writerow(aggregated_data[interval])


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

    write_to_json(experiment, args.json_file)
    write_to_csv(experiment, args.json_file)

    final_data = experiment.analyzer_data["aggregated"][experiment.intervals - 1]
    for data in final_data:
        if "interval" in data:
            continue
        print("{}:\t{}".format(data, final_data[data]))


if __name__ == '__main__':
    main()
