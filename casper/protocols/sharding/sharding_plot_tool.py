"""The blockchain plot tool implements functions for plotting sharded blockchain data structures"""

from casper.plot_tool import PlotTool
from casper.safety_oracles.clique_oracle import CliqueOracle
import casper.utils as utils


class ShardingPlotTool(PlotTool):
    """The module contains functions for plotting a blockchain data structure"""

    def __init__(self, display, save, view, validator_set):
        super().__init__(display, save, 's')
        self.view = view
        self.validator_set = validator_set
        self.starting_blocks = self.view.starting_blocks
        self.message_fault_tolerance = dict()

        self.blockchain = []
        self.communications = []

        self.block_fault_tolerance = {}
        self.message_labels = {}
        self.justifications = {
            validator: []
            for validator in validator_set
        }

    def update(self, new_messages=None):
        """Updates displayable items with new messages and paths"""
        return

        if new_messages is None:
            new_messages = []

        self._update_new_justifications(new_messages)
        self._update_blockchain(new_messages)
        self._update_block_fault_tolerance()
        self._update_message_labels(new_messages)

    def plot(self):
        """Builds relevant edges to display and creates next viewgraph using them"""
        return
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
        best_chain = utils.build_chain(best_message, None)[:-1]
        return utils.edge(best_chain, 5, 'red', 'solid')

    def get_validator_chains(self):
        """Returns a list of edges main from validators current forkchoice to genesis"""
        vals_chain_edges = []
        for validator in self.validator_set:
            chain = utils.build_chain(validator.my_latest_message(), None)[:-1]
            vals_chain_edges.append(utils.edge(chain, 2, 'blue', 'solid'))

        return vals_chain_edges

    def _update_new_justifications(self, new_messages):
        for message in new_messages:
            sender = message.sender
            for validator in message.justification:
                last_message = self.view.justified_messages[message.justification[validator]]
                # only show if new justification
                if last_message not in self.justifications[sender]:
                    self.communications.append([last_message, message])
                    self.justifications[sender].append(last_message)

    def _update_blockchain(self, new_messages):
        for message in new_messages:
            if message.estimate is not None:
                self.blockchain.append([message, message.estimate])

    def _update_message_labels(self, new_messages):
        for message in new_messages:
            self.message_labels[message] = message.sequence_number

    def _update_block_fault_tolerance(self):
        tip = self.view.estimate()

        while tip and self.block_fault_tolerance.get(tip, 0) != len(self.validator_set) - 1:
            oracle = CliqueOracle(tip, self.view, self.validator_set)
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.block_fault_tolerance[tip] = num_node_ft

            tip = tip.estimate
