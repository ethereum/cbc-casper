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
        sim_rounds,
        sim_report_interval
    ):
        self.name = name
        self.data = data
        self.num_simulations = num_simulations
        self.validator_set_generator = validator_set_generator
        self.msg_mode = msg_mode
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
        print(self.analyzer_data)
        self._output()

    def run_sim(self, sim_id):
        validator_set = self.validator_set_generator()
        runner = SimulationRunner(
            validator_set,
            message_maker(self.msg_mode),
            total_rounds=self.sim_rounds,
            report_interval=self.sim_report_interval
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
        for d in self.data:
            interval_list = [
                self.analyzer_data['simulation_data'][sim_id][interval][d]
                for sim_id in self.analyzer_data['simulation_data']
            ]
            for stat in self.INTERVAL_STATS:
                key = "{}-{}".format(d, stat)
                aggregated_interval[key] = getattr(statistics, stat)(interval_list)

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

    def _output(self):
        if not os.path.exists("out"):
            os.makedirs("out")
        if not os.path.exists("out/{}".format(self.name)):
            os.makedirs("out/{}".format(self.name))

        self._output_json()
        self._output_csv()

    def _output_json(self):
        with open("{}/{}.json".format(self.output_dir, self.name), 'w') as f:
            json.dump(self.analyzer_data, f, indent=4)

    def _output_csv(self):
        with open("{}/{}.csv".format(self.output_dir, self.name), 'w') as csvfile:
            aggregated_data = self.analyzer_data["aggregated"]
            writer = csv.DictWriter(csvfile, fieldnames=aggregated_data[0].keys())

            writer.writeheader()
            for interval in aggregated_data:
                writer.writerow(aggregated_data[interval])

    @property
    def output_dir(self):
        return "out/{}".format(self.name)
