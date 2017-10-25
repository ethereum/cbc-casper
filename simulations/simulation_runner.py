import sys

import casper.utils as utils
from casper.network import Network
from casper.safety_oracles.clique_oracle import CliqueOracle


class SimulationRunner:
    def __init__(
            self,
            validator_set,
            msg_gen,
            total_rounds,
            report=False,
            report_interval=20
    ):
        self.validator_set = validator_set
        self.msg_gen = msg_gen
        self.report = report
        self.report_interval = report_interval

        self.round = 0
        if total_rounds:
            self.total_rounds = total_rounds
        else:
            self.total_rounds = sys.maxsize

        self.blockchain = []
        self.communications = []
        self.safe_blocks = []
        self.node_ft = {}

        self.network = Network(validator_set)
        self.network.random_initialization()
        if self.report:
            self.network.report()

    def run(self):
        """ run simulation total_rounds if specified
            otherwise, run indefinitely """
        while self.round < self.total_rounds:
            self.step()

    def step(self):
        """ run one round of the simulation """
        self.round += 1
        message_paths = self.msg_gen(self.validator_set)

        affected_validators = {j for i, j in message_paths}

        sent_messages = self._send_messages_along_paths(message_paths)
        new_messages = self._make_new_messages(affected_validators)
        self._check_messages_for_safety(new_messages)

        self._update_communications(message_paths, sent_messages, new_messages)
        self._update_safe_messages()
        if self.report and self.round % self.report_interval == self.report_interval - 1:
            self.plot()

    def plot(self):
        # Build the global forkchoice, so we can display it!
        best_message = self.network.global_view.estimate()
        best_chain = utils.build_chain(best_message, None)

        # Build each validators forkchoice, so we can display as well!
        vals_chain = []
        for validator in self.validator_set:
            vals_chain.append(
                utils.build_chain(validator.my_latest_message(), None)
            )

        edgelist = []
        edgelist.append(utils.edge(self.blockchain, 2, 'grey', 'solid'))
        edgelist.append(utils.edge(self.communications, 1, 'black', 'dotted'))
        edgelist.append(utils.edge(best_chain, 5, 'red', 'solid'))
        for chains in vals_chain:
            edgelist.append(utils.edge(chains, 2, 'blue', 'solid'))

        self.network.report(
            edges=edgelist,
            colored_messages=self.safe_blocks,
            color_mag=self.node_ft
        )

    def _send_messages_along_paths(self, message_paths):
        sent_messages = {}
        # Send most recent message of sender to receive
        for sender, receiver in message_paths:
            message = sender.my_latest_message()
            self.network.propagate_message_to_validator(message, receiver)
            sent_messages[sender] = message

        return sent_messages

    def _make_new_messages(self, validators):
        messages = {}
        for validator in validators:
            message = self.network.get_message_from_validator(validator)
            messages[validator] = message
            # Update display to show this new message properly
            if message.estimate is not None:
                self.blockchain.append([message, message.estimate])

        return messages

    def _check_messages_for_safety(self, messages):
        for validator in messages:
            message = messages[validator]

            # Have validators try to find newly finalized blocks
            curr = message
            last_finalized_block = validator.view.last_finalized_block
            while curr != last_finalized_block:
                if validator.check_estimate_safety(curr):
                    break
                curr = curr.estimate

    def _update_communications(self, message_paths, sent_messages, new_messages):
        for sender, receiver in message_paths:
            self.communications.append([sent_messages[sender], new_messages[receiver]])

    def _update_safe_messages(self):
        # Display the fault tolerance in the global view
        tip = self.network.global_view.estimate()
        while tip and self.node_ft.get(tip, 0) != len(self.validator_set) - 1:
            # TODO: decide which oracle to use when displaying global ft.
            # When refactoring visualizations, could give options to switch
            # between different oracles while displaying a view!
            oracle = CliqueOracle(tip, self.network.global_view, self.validator_set)
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.safe_blocks.append(tip)
                self.node_ft[tip] = num_node_ft

            tip = tip.estimate
