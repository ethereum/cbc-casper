"""The blockchain plot tool implements functions for plotting blockchain data structures"""

from casper.plot_tool import PlotTool
from casper.safety_oracles.clique_oracle import CliqueOracle
import casper.utils as utils


class BlockchainPlotTool(PlotTool):
    """The module contains functions for plotting a blockchain data structure"""

    def __init__(self, display, save, view, validator_set):
        super().__init__(display, save)
        self.view = view
        self.validator_set = validator_set
        self.message_fault_tolerance = dict()

        self.blockchain = []
        self.communications = []
        self.block_fault_tolerance = {}
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
        self._update_blockchain(new_messages)
        self._update_block_fault_tolerance()
        self._update_message_labels(new_messages)

    def plot(self):
        """Builds relevant edges to display and creates next viegraph using them"""
        best_chain_edge = self.get_best_chain()

        validator_chain_edges = self.get_validator_chains()

        edgelist = []
        edgelist.append(utils.edge(self.blockchain, 2, 'grey', 'solid'))
        edgelist.append(utils.edge(self.communications, 1, 'black', 'dotted'))
        edgelist.append(best_chain_edge)
        edgelist.extend(validator_chain_edges)

        self.next_viewgraph(
            self.view,
            self.validator_set,
            edges=edgelist,
            message_colors=self.block_fault_tolerance,
            message_labels=self.message_labels
        )

    def get_best_chain(self):
        """Returns an edge made of the global forkchoice to genesis"""
        best_message = self.view.estimate()
        best_chain = utils.build_chain(best_message, None)
        return utils.edge(best_chain, 5, 'red', 'solid')

    def get_validator_chains(self):
        """Returns a list of edges main from validators current forkchoice to genesis"""
        vals_chain_edges = []
        for validator in self.validator_set:
            chain = utils.build_chain(validator.my_latest_message(), None)
            vals_chain_edges.append(utils.edge(chain, 2, 'blue', 'solid'))

        return vals_chain_edges

    def _update_communications(self, message_paths, sent_messages, new_messages):
        for sender, receiver in message_paths:
            self.communications.append([sent_messages[sender], new_messages[receiver]])

    def _update_blockchain(self, new_messages):
        for message in new_messages.values():
            if message.estimate is not None:
                self.blockchain.append([message, message.estimate])

    def _update_message_labels(self, new_messages):
        for message in new_messages.values():
            self.message_labels[message] = message.sequence_number

    def _update_block_fault_tolerance(self):
        tip = self.view.estimate()

        while tip and self.block_fault_tolerance.get(tip, 0) != len(self.validator_set) - 1:
            oracle = CliqueOracle(tip, self.view, self.validator_set)
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.block_fault_tolerance[tip] = num_node_ft

            tip = tip.estimate
