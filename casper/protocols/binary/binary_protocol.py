import json

from casper.utils import get_random_str
from casper.protocol import Protocol
# binary is a degenerate case of integer, so we can use integer view/estimator
from casper.protocols.integer.integer_view import IntegerView
from casper.protocols.binary.bet import Bet
from casper.protocols.integer.integer_plot_tool import IntegerPlotTool


class BinaryProtocol(Protocol):
    PlotTool = IntegerPlotTool

    def __init__(self, json_string, display, save, report_interval):
        parsed_json = self.parse_json(json_string)

        super().__init__(
            parsed_json['config']['validators'],
            parsed_json['execution']['execution_string'],
            parsed_json['execution']['msg_per_round'] * report_interval,
            display,
            save,
            IntegerPlotTool,
            IntegerView,
            Bet
        )

        self.set_initial_messages(parsed_json['config']['initial_estimates'])

        self.plot_tool.plot()

    @classmethod
    def parse_json(cls, json_string):
        parsed_json = json.loads(json_string)

        assert parsed_json['protocol'] == 'binary'

        config = parsed_json['config']
        assert len(config['validators']) == len(config['initial_estimates'])

        for estimate in config['initial_estimates']:
            assert estimate in {0, 1}

        return parsed_json

    def set_initial_messages(self, initial_estimates):
        for validator in self.global_validator_set:
            initial_message = Bet(
                initial_estimates[validator.name],
                dict(),
                validator,
                0,
                0
            )

            self.register_message(initial_message, get_random_str(10))
            validator.initialize_view([initial_message])
