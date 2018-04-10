import json
import random as r

from casper.utils import get_random_str
from casper.protocol import Protocol
from casper.protocols.concurrent.concurrent_view import ConcurrentView
from casper.protocols.concurrent.block import Block
from casper.protocols.concurrent.concurrent_plot_tool import ConcurrentPlotTool


class ConcurrentProtocol(Protocol):
    """A protocol for coming to consensus on a concurrent schedule"""
    Message = Block
    View = ConcurrentView
    PlotTool = ConcurrentPlotTool

    def __init__(self, json_string, display, save, report_interval):
        parsed_json = self.parse_json(json_string)

        super().__init__(
            parsed_json['config']['validators'],
            parsed_json['execution']['execution_string'],
            parsed_json['execution']['msg_per_round'] * report_interval,
            display,
            save,
            ConcurrentPlotTool,
            ConcurrentView,
            Block
        )

        self.select_rules = dict()
        self.create_rules = dict()
        self.select_rules['random'] = self.select_random_outputs_to_consume
        self.create_rules['random'] = self.create_random_new_outputs

        self.set_initial_messages(
            parsed_json['config']['genesis_estimate'],
            parsed_json['config']['create_outputs']
        )

        self.initialize_rewrite_rules(
            parsed_json['config']['select_outputs'],
            parsed_json['config']['create_outputs']
        )

        self.plot_tool.plot()

    @staticmethod
    def parse_json(json_string):
        parsed_json = json.loads(json_string)

        assert parsed_json['protocol'] == 'concurrent'

        config = parsed_json['config']

        assert set(config['genesis_estimate']).issubset(set(config['starting_outputs']))

        return parsed_json

    def set_initial_messages(self, genesis_estimate, create_name):
        validator = self.global_validator_set.get_validator_by_name(0)

        blocks = set([None])
        inputs = set([int(i) for i in genesis_estimate])
        outputs = self.create_rules[create_name](inputs, len(inputs))
        estimate = {'blocks': blocks, 'inputs': inputs, 'outputs': outputs}

        initial_message = Block(estimate, dict(), validator, -1, 0)
        self.register_message(initial_message, get_random_str(10))

        for validator in self.global_validator_set:
            validator.initialize_view([initial_message])

    def initialize_rewrite_rules(self, select_name, create_name):
        select_func = self.select_rules[select_name]
        create_func = self.create_rules[create_name]

        for validator in self.global_validator_set:
            validator.view.set_rewrite_rules(select_func, create_func)

        self.global_view.set_rewrite_rules(select_func, create_func)

    def select_random_outputs_to_consume(self, available_outputs, output_sources):
        num_outputs = r.randint(1, len(available_outputs))
        return set(r.sample(available_outputs, num_outputs))

    def create_random_new_outputs(self, old_outputs, num_new_outputs):
        return set([r.randint(0, 1000000000) for _ in range(num_new_outputs)])
