import json
import random as r

from casper.utils import get_random_str
from casper.protocol import Protocol
from casper.protocols.blockchain.blockchain_view import BlockchainView
from casper.protocols.blockchain.block import Block
from casper.protocols.blockchain.blockchain_plot_tool import BlockchainPlotTool


class BlockchainProtocol(Protocol):
    PlotTool = BlockchainPlotTool

    def __init__(self, json_string, display, save, report_interval):
        parsed_json = self.parse_json(json_string)

        super().__init__(
            parsed_json['config']['validators'],
            parsed_json['execution']['execution_string'],
            parsed_json['execution']['msg_per_round'] * report_interval,
            display,
            save,
            BlockchainPlotTool,
            BlockchainView,
            Block
        )

        self.set_initial_messages()

        self.plot_tool.plot()

    @staticmethod
    def parse_json(json_string):
        parsed_json = json.loads(json_string)

        assert parsed_json['protocol'] == 'blockchain'

        return parsed_json

    def set_initial_messages(self):
        initial_message = Block(
            None, dict(), self.global_validator_set.get_validator_by_name(0), -1, 0
        )
        self.register_message(initial_message, get_random_str(10))

        for validator in self.global_validator_set:
            validator.initialize_view([initial_message])
