"""The concurrent plot tool implements functions for plotting concurrent data structures"""

from casper.plot_tool import PlotTool
import casper.utils as utils


class ConcurrentPlotTool(PlotTool):
    """The module contains functions for plotting a concurrent data structure"""

    def __init__(self, display, save, view, validator_set):
        super().__init__(display, save, 's')
        self.view = view
        self.validator_set = validator_set
        self.genesis_block = self.view.genesis_block
        self.message_fault_tolerance = dict()

        self.schedule = []
        self.communications = []

        self.block_fault_tolerance = {}
        self.message_labels = {}
        self.justifications = {
            validator: []
            for validator in validator_set
        }

        self.message_labels[self.genesis_block] = "G"

    def update(self, new_messages=None):
        """Updates displayable items with new messages and paths"""
        if new_messages is None:
            new_messages = []

        self._update_new_justifications(new_messages)
        self._update_schedule(new_messages)
        self._update_block_fault_tolerance()
        self._update_message_labels(new_messages)

    def plot(self):
        """Builds relevant edges to display and creates next viewgraph using them"""

        best_schedule_edge = self.get_best_schedule()

        validator_chain_edges = self.get_validator_chains()

        edgelist = []
        edgelist.append(utils.edge(self.schedule, 2, 'grey', 'solid'))
        edgelist.append(utils.edge(self.communications, 1, 'black', 'dotted'))
        edgelist.append(best_schedule_edge)
        edgelist.extend(validator_chain_edges)

        self.next_viewgraph(
            self.view,
            self.validator_set,
            edges=edgelist,
            message_colors=self.block_fault_tolerance,
            message_labels=self.message_labels
        )

    def get_best_schedule(self):
        """Returns an edge made of the global forkchoice to genesis"""
        best_messages = self.view.estimate()['blocks']
        best_schedule = utils.build_schedule(best_messages)
        return utils.edge(best_schedule, 5, 'red', 'solid')

    def get_validator_chains(self):
        """Returns a list of edges main from validators current forkchoice to genesis"""
        vals_chain_edges = []
        for validator in self.validator_set:
            chain = utils.build_schedule(set([validator.my_latest_message()]))
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

    def _update_schedule(self, new_messages):
        for message in new_messages:
            for ancestor in message.estimate['blocks']:
                if ancestor is not None:
                    self.schedule.append([message, ancestor])

    def _update_message_labels(self, new_messages):
        for message in new_messages:
            self.message_labels[message] = message.sequence_number

    def _update_block_fault_tolerance(self):
        return
