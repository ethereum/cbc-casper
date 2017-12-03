"""The binary plot tool implements functions for plotting binary consensus"""

from casper.plot_tool import PlotTool
from casper.safety_oracles.clique_oracle import CliqueOracle
import casper.utils as utils


class IntegerPlotTool(PlotTool):
    """The module contains functions for plotting a binary data structure"""

    def __init__(self, display, save, view, validator_set):
        super().__init__(display, save, 'o')
        self.view = view
        self.validator_set = validator_set

        self.communications = []
        self.self_communications = []
        self.bet_fault_tolerance = {}
        self.message_labels = {}

        self.first_time = True

    def update(self, message_paths=None, sent_messages=None, new_messages=None):
        """Updates displayable items with new messages and paths"""
        if message_paths is None:
            message_paths = []
        if sent_messages is None:
            sent_messages = dict()
        if new_messages is None:
            new_messages = dict()

        self._update_communications(message_paths, sent_messages, new_messages)
        self._update_self_communications(new_messages)
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

    def _update_communications(self, message_paths, sent_messages, new_messages):
        for sender, receiver in message_paths:
            self.communications.append([sent_messages[sender], new_messages[receiver]])

    def _update_self_communications(self, new_messages):
        for validator in new_messages:
            message = new_messages[validator]

            if validator in message.justification:
                last_message = self.view.justified_messages[message.justification[validator]]
                self.self_communications.append([last_message, message])

    def _update_message_labels(self, new_messages):
        for message in new_messages.values():
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
