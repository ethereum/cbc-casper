"""The binary plot tool implements functions for plotting binary consensus"""

from casper.plot_tool import PlotTool
from casper.safety_oracles.clique_oracle import CliqueOracle
import casper.utils as utils


class BinaryPlotTool(PlotTool):
    """The module contains functions for plotting a binary data structure"""

    def __init__(self, display, save, view, validator_set):
        super().__init__(display, save)
        self.view = view
        self.validator_set = validator_set

        self.communications = []
        self.bet_fault_tolerance = {}
        self.message_labels = {}


    def update(self, message_paths=None, sent_messages=None, new_messages=None):
        """Updates displayable items with new messages and paths"""
        if message_paths is None:
            message_paths = []
        if sent_messages is None:
            sent_messages = dict()
        if new_messages is None:
            new_messages = dict()

        self._update_communications(message_paths, sent_messages, new_messages)
        self._update_message_fault_tolerance()
        self._update_message_labels(new_messages)

    def plot(self):
        """Builds relevant edges to display and creates next viegraph using them"""
        edgelist = []
        edgelist.append(utils.edge(self.communications, 1, 'black', 'dotted'))

        self.next_viewgraph(
            self.view,
            self.validator_set,
            edges=edgelist,
            message_colors=self.bet_fault_tolerance,
            message_labels=self.message_labels
        )


    def _update_communications(self, message_paths, sent_messages, new_messages):
        for sender, receiver in message_paths:
            self.communications.append([sent_messages[sender], new_messages[receiver]])


    def _update_message_labels(self, new_messages):
        for message in new_messages.values():
            self.message_labels[message] = message.estimate

    def _update_message_fault_tolerance(self):
        for bet in self.view.values():
            oracle = CliqueOracle(bet, self.view, self.validator_set)
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.bet_fault_tolerance[bet] = num_node_ft
