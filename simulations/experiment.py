from simulations.analyzer import Analyzer
from simulations.simulation_runner import SimulationRunner
from simulations.utils import (
    message_maker,
)


class Experiment:
    def __init__(
        self,
        data,
        num_simulations,
        validator_set_generator,
        msg_mode,
        sim_rounds,
        sim_report_interval
    ):
        self.data = data
        self.num_simulations = num_simulations
        self.validator_set_generator = validator_set_generator
        self.msg_mode = msg_mode
        self.sim_rounds = sim_rounds
        self.sim_report_interval = sim_report_interval

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

    def run_sim(self, sim_id):
        validator_set = self.validator_set_generator()
        runner = SimulationRunner(
            validator_set,
            message_maker(self.msg_mode),
            total_rounds=self.sim_rounds,
            report_interval=self.sim_report_interval
        )
        for interval in range(int(runner.total_rounds / runner.report_interval)):
            for step in range(runner.report_interval):
                runner.step()

            self._collect_data(runner, sim_id, interval)
        self._collect_data(runner, sim_id, "final")

    def _aggregate_data(self):
        aggregated = {
            interval: self._aggregate_interval_data(interval)
            for interval in range(int(self.sim_rounds / self.sim_report_interval))
        }
        aggregated["final"] = self._aggregate_interval_data("final")
        self.analyzer_data["aggregated"] = aggregated

    def _aggregate_interval_data(self, interval):
        return {
            d: [
                self.analyzer_data['simulation_data'][sim_id][interval][d]
                for sim_id in self.analyzer_data['simulation_data']
            ]
            for d in self.data
        }

    def _collect_data(self, runner, sim_id, interval):
        if sim_id not in self.analyzer_data["simulation_data"]:
            self.analyzer_data['simulation_data'][sim_id] = {}

        analyzer = Analyzer(runner)
        self.analyzer_data['simulation_data'][sim_id][interval] = {
            d: getattr(analyzer, d)()
            for d in self.data
        }
