"""The integer plot tool implements functions for plotting integer consensus"""

from casper.plot_tool import PlotTool
from casper.safety_oracles.clique_oracle import CliqueOracle
import casper.utils as utils


class IntegerPlotTool(PlotTool):
    """The module contains functions for plotting an integer data structure"""

    def __init__(self, display, save, view, validator_set):
        super().__init__(display, save, 'o')
        self.view = view
        self.validator_set = validator_set

        self.communications = []
        self.self_communications = []
        self.bet_fault_tolerance = {}
        self.message_labels = {}
        self.justifications = {
            validator: []
            for validator in validator_set
        }

        self.first_time = True

    def update(self, new_messages=None, received_messages=None):
        """Updates displayable items with new messages and paths"""
        if new_messages is None:
            new_messages = []
        if received_messages is None:
            received_messages = {}

        self._update_new_justifications(new_messages)
        self._update_message_fault_tolerance()
        self._update_message_labels(new_messages)

    def plot(self):
        """Builds relevant edges to display and creates next viegraph using them"""
        if self.first_time:
            self._update_first_message_labels()
            self.first_time = False

        edgelist = []
        edgelist.append(utils.edge(self.communications, 1, 'black', 'solid'))
        edgelist.append(utils.edge(self.self_communications, 1, 'black', 'solid'))

        self.next_viewgraph(
            self.view,
            self.validator_set,
            edges=edgelist,
            message_colors=self.bet_fault_tolerance,
            message_labels=self.message_labels
        )

    def _update_first_message_labels(self):
        for message in self.view.justified_messages.values():
            self.message_labels[message] = message.estimate

    def _update_new_justifications(self, new_messages):
        for message in new_messages:
            validator = message.sender
            for validator in message.justification:
                last_message = self.view.justified_messages[message.justification[validator]]
                # only show if new justification
                if last_message not in self.justifications[validator]:
                    self.self_communications.append([last_message, message])
                    self.justifications[validator].append(last_message)
                # always show self as justification
                elif last_message.sender == message.sender:
                    self.self_communications.append([last_message, message])

    def _update_message_labels(self, new_messages):
        for message in new_messages:
            self.message_labels[message] = message.estimate

    def _update_message_fault_tolerance(self):
        for validator in self.view.latest_messages:

            latest_message = self.view.latest_messages[validator]

            if latest_message in self.bet_fault_tolerance:
                continue

            oracle = CliqueOracle(latest_message, validator.view, self.validator_set)
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.bet_fault_tolerance[latest_message] = num_node_ft
