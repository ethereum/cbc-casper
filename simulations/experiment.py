import csv
import json
import os
import statistics

from simulations.analyzer import Analyzer
from simulations.simulation_runner import SimulationRunner
from simulations.utils import (
    message_maker,
)


class Experiment:
    INTERVAL_STATS = ["mean", "stdev"]

    def __init__(
            self,
            name,
            data,
            num_simulations,
            validator_set_generator,
            msg_mode,
            protocol,
            sim_rounds,
            sim_report_interval
    ):
        self.name = name
        self.data = data
        self.num_simulations = num_simulations
        self.validator_set_generator = validator_set_generator
        self.msg_mode = msg_mode
        self.protocol = protocol
        self.sim_rounds = sim_rounds
        self.sim_report_interval = sim_report_interval
        self.intervals = int(self.sim_rounds / self.sim_report_interval)

        self.sim_number = 0
        self.analyzer_data = {'simulation_data': {}}

    def run(self):
        print("Running", end='')
        while self.sim_number < self.num_simulations:
            self.run_sim(self.sim_number)
            self.sim_number += 1
            print(".", end='', flush=True)

        print(" complete!")

        self._aggregate_data()

    def run_sim(self, sim_id):
        validator_set = self.validator_set_generator()
        runner = SimulationRunner(
            validator_set,
            message_maker(self.msg_mode),
            self.protocol,
            total_rounds=self.sim_rounds,
            report_interval=self.sim_report_interval,
            display=False,
            save=False
        )
        for interval in range(self.intervals):
            for step in range(runner.report_interval):
                runner.step()

            self._collect_data(runner, sim_id, interval)

    def _aggregate_data(self):
        aggregated = {
            interval: self._aggregate_interval_data(interval)
            for interval in range(self.intervals)
        }
        self.analyzer_data["aggregated"] = aggregated

    def _aggregate_interval_data(self, interval):
        aggregated_interval = {}
        for data in self.data:
            interval_list = [
                self.analyzer_data['simulation_data'][sim_id][interval][data]
                for sim_id in self.analyzer_data['simulation_data']
                if self.analyzer_data['simulation_data'][sim_id][interval][data]
            ]
            for stat in self.INTERVAL_STATS:
                key = "{}-{}".format(data, stat)
                if len(interval_list) > 1:
                    aggregated_interval[key] = getattr(statistics, stat)(interval_list)
                else:
                    aggregated_interval[key] = None

        aggregated_interval['interval'] = interval
        return aggregated_interval

    def _collect_data(self, runner, sim_id, interval):
        if sim_id not in self.analyzer_data["simulation_data"]:
            self.analyzer_data['simulation_data'][sim_id] = {}

        analyzer = Analyzer(runner)
        self.analyzer_data['simulation_data'][sim_id][interval] = {
            d: getattr(analyzer, d)()
            for d in self.data

        }

    def output_results(self):
        self._make_output_dir()

        self._output_json()
        self._output_csv()

    def store_copy_config(self, config):
        self._make_output_dir()

        with open("{}/config.json".format(self.output_dir), 'w') as f:
            json.dump(config, f, indent=4)

    def _make_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _output_json(self):
        with open("{}/out.json".format(self.output_dir), 'w') as f:
            json.dump(self.analyzer_data, f, indent=4)

    def _output_csv(self):
        with open("{}/out.csv".format(self.output_dir), 'w') as csvfile:
            aggregated_data = self.analyzer_data["aggregated"]
            writer = csv.DictWriter(csvfile, fieldnames=aggregated_data[0].keys())

            writer.writeheader()
            for interval in aggregated_data:
                writer.writerow(aggregated_data[interval])

    @property
    def output_dir(self):
        return "out/{}".format(self.name)
