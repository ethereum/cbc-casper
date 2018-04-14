import json

from casper.utils import get_random_str
from casper.protocol import Protocol
from casper.protocols.order.order_view import OrderView
from casper.protocols.order.bet import Bet
from casper.protocols.order.order_plot_tool import OrderPlotTool


class OrderProtocol(Protocol):
    """A protocol for coming to consensus on a list of known elements"""
    Message = Bet
    View = OrderView
    PlotTool = OrderPlotTool

    def __init__(self, json_string, display, save, report_interval):
        parsed_json = self.parse_json(json_string)

        super().__init__(
            parsed_json['config']['validators'],
            parsed_json['execution']['execution_string'],
            parsed_json['execution']['msg_per_round'] * report_interval,
            display,
            save,
            OrderPlotTool,
            OrderView,
            Bet
        )

        self.set_initial_messages(parsed_json['config']['initial_estimates'])

        self.plot_tool.plot()

    @staticmethod
    def parse_json(json_string):
        parsed_json = json.loads(json_string)

        assert parsed_json['protocol'] == 'order'

        config = parsed_json['config']
        assert len(config['validators']) == len(config['initial_estimates'])

        all_items = set()
        for estimate in config['initial_estimates']:
            assert isinstance(estimate, list)
            assert len(estimate) == len(set(estimate))
            all_items.update(estimate)

        for estimate in config['initial_estimates']:
            assert len(set(estimate).union(all_items)) == len(all_items)

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

        self.plot_tool.plot()
