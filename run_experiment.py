import argparse
import json
import os

from datetime import datetime
import calendar

from simulations.experiment import Experiment
from simulations.utils import (
    select_protocol,
    validator_generator
)


def timestamp():
    d = datetime.utcnow()
    return str(calendar.timegm(d.utctimetuple()))


def main():
    parser = argparse.ArgumentParser(description='Run CasperCBC standard simulations.')
    parser.add_argument(
        'json_file', metavar='J', type=str,
        help='specifies the json file with the experiment params'
    )

    args = parser.parse_args()

    with open(args.json_file) as f:
        config = json.load(f)

    base_name = os.path.basename(args.json_file)
    file_name = os.path.splitext(base_name)[0]

    experiment_name = "{}-{}".format(file_name, timestamp())
    protocol = select_protocol(config['protocol'])

    experiment = Experiment(
        experiment_name,
        config['data'],
        config['num_simulations'],
        validator_generator(config['validator_info'], protocol),
        config['msg_mode'],
        protocol,
        config['rounds_per_sim'],
        config['report_interval']
    )

    experiment.run()
    experiment.output_results()
    experiment.store_copy_config(config)

    final_data = experiment.analyzer_data["aggregated"][experiment.intervals - 1]
    for data in final_data:
        if "interval" in data:
            continue
        print("{}:\t{}".format(data, final_data[data]))

    print()
    print("Output written to: {}/".format(experiment.output_dir))


if __name__ == '__main__':
    main()
