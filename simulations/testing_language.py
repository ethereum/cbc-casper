"""The testing language module ... """
import re
import random as r

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.plot_tool import PlotTool
from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.validator_set import ValidatorSet
import casper.utils as utils

from simulations.networks.simple_networks import NoDelayNetwork


class TestLangCBC(object):
    """Allows testing of simulation scenarios with small testing language."""

    # Signal to py.test that TestLangCBC should not be discovered.
    __test__ = False

    TOKEN_PATTERN = '([A-Za-z]*)([0-9]*)([-]*)([A-Za-z0-9]*)'

    def __init__(self, val_weights, protocol=BlockchainProtocol, display=False):

        self.validator_set = ValidatorSet(val_weights, protocol)
        self.display = display
        self.network = NoDelayNetwork(self.validator_set, protocol)

        self.plot_tool = PlotTool(display, False, 's')
        self.blocks = dict()
        self.blockchain = []
        self.communications = []
        self.block_fault_tolerance = dict()

        # Register token handlers.
        self.handlers = dict()
        self.handlers['B'] = self.make_block
        self.handlers['S'] = self.send_all_blocks
        self.handlers['P'] = self.send_only_block
        self.handlers['C'] = self.check_safety
        self.handlers['U'] = self.no_safety
        self.handlers['H'] = self.check_head_equals_block
        self.handlers['RR'] = self.round_robin
        self.handlers['R'] = self.report

    def _validate_validator(self, validator):
        if validator not in self.validator_set:
            raise ValueError('Validator {} does not exist'.format(validator))

    def _validate_block_exists(self, block_name):
        if block_name not in self.blocks:
            raise ValueError('Block {} does not exist'.format(block_name))

    def _validate_block_does_not_exist(self, block_name):
        if block_name in self.blocks:
            raise ValueError('Block {} already exists'.format(block_name))

    def _blocks_needed_to_justify(self, block, validator):
        messages_needed = set()

        current_block_hashes = set()
        for block_hash in block.justification.values():
            if block_hash not in validator.view.pending_messages and \
               block_hash not in validator.view.justified_messages:
                current_block_hashes.add(block_hash)

        while any(current_block_hashes):
            next_hashes = set()

            for block_hash in current_block_hashes:
                block = self.network.global_view.justified_messages[block_hash]
                messages_needed.add(block)

                for other_hash in block.justification.values():
                    if other_hash not in validator.view.pending_messages and \
                       other_hash not in validator.view.justified_messages:
                        next_hashes.add(other_hash)

            current_block_hashes = next_hashes

        return messages_needed

    def _propagate_message_to_validator(self, block, validator):
        self.network.send(validator, block)
        received_message = self.network.receive(validator)
        if received_message:
            validator.receive_messages(set([received_message]))

    def parse(self, test_string):
        """Parse the test_string, and run the test"""
        for token in test_string.split(' '):
            letter, validator, dash, name = re.match(self.TOKEN_PATTERN, token).groups()
            if letter+validator+dash+name != token:
                raise ValueError("Bad token: %s" % token)
            if validator != '':
                try:
                    validator = self.validator_set.get_validator_by_name(int(validator))
                except KeyError:
                    raise ValueError("Validator {} does not exist".format(validator))

            self.handlers[letter](validator, name)

    def send_all_blocks(self, validator, block_name):
        """Send some validator a block, and all unseen messages in its justification."""
        self._validate_validator(validator)
        self._validate_block_exists(block_name)

        block = self.blocks[block_name]
        if block.hash in validator.view.justified_messages:
            raise Exception("Validator has already seen block")
        self._propagate_message_to_validator(block, validator)

        blocks_to_send = self._blocks_needed_to_justify(block, validator)
        for block in blocks_to_send:
            self._propagate_message_to_validator(block, validator)

        assert block.hash not in validator.view.pending_messages
        assert block.hash not in validator.view.num_missing_dependencies
        assert self.blocks[block_name].hash in validator.view.justified_messages

    def send_only_block(self, validator, block_name):
        """Send some validator a block."""
        self._validate_validator(validator)
        self._validate_block_exists(block_name)

        block = self.blocks[block_name]
        if block.hash in validator.view.justified_messages:
            raise Exception("Validator has already seen block")

        self._propagate_message_to_validator(block, validator)

    def make_block(self, validator, block_name):
        """Have some validator produce a block."""
        self._validate_validator(validator)
        self._validate_block_does_not_exist(block_name)

        new_block = validator.make_new_message()
        self.network.global_view.add_messages(
            set([new_block])
        )

        if new_block.estimate is not None:
            self.blockchain.append([new_block, new_block.estimate])

        self.blocks[block_name] = new_block

    def round_robin(self, validator, block_name):
        """Have each validator create a block in a perfect round robin."""
        self._validate_validator(validator)
        self._validate_block_does_not_exist(block_name)

        # start round robin at validator speicied by validator in args
        validators = self.validator_set.sorted_by_name()
        start_index = validators.index(validator)
        validators = validators[start_index:] + validators[:start_index]

        for i in range(len(self.validator_set)):
            if i == len(self.validator_set) - 1:
                name = block_name
            else:
                name = r.random()
            maker = validators[i]
            receiver = validators[(i + 1) % len(validators)]

            self.make_block(maker, name)
            self.send_all_blocks(receiver, name)

    def check_safety(self, validator, block_name):
        """Check that some validator detects safety on a block."""
        self._validate_validator(validator)
        self._validate_block_exists(block_name)

        block = self.blocks[block_name]
        validator.update_safe_estimates()

        assert validator.view.last_finalized_block is None or \
            not block.conflicts_with(validator.view.last_finalized_block), \
            "Block {0} failed safety assert for validator-{1}".format(block_name, validator.name)

    def no_safety(self, validator, block_name):
        """Check that some validator does not detect safety on a block."""
        self._validate_validator(validator)
        self._validate_block_exists(block_name)

        block = self.blocks[block_name]
        validator.update_safe_estimates()

        # NOTE: This should never fail
        assert validator.view.last_finalized_block is None or \
            block.conflicts_with(validator.view.last_finalized_block), \
            "Block {} failed no-safety assert".format(block_name)

    def check_head_equals_block(self, validator, block_name):
        """Check some validators forkchoice is the correct block."""
        self._validate_validator(validator)
        self._validate_block_exists(block_name)

        block = self.blocks[block_name]

        head = validator.view.estimate()

        assert block == head, "Validator {} does not have " \
                              "block {} at head".format(validator, block_name)

    def report(self, num, name):
        """Display the view graph of the current global_view"""
        assert num == name and num == '', "...no validator or number needed to report!"

        if not self.display:
            return

        # Update the safe blocks!
        tip = self.network.global_view.estimate()
        while tip and self.block_fault_tolerance.get(tip, 0) != len(self.validator_set) - 1:
            oracle = CliqueOracle(tip, self.network.global_view, self.validator_set)
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.block_fault_tolerance[tip] = num_node_ft

            tip = tip.estimate

        edgelist = []

        best_chain = utils.build_chain(
            self.network.global_view.estimate(),
            None
        )
        edgelist.append(utils.edge(best_chain, 5, 'red', 'solid'))

        for validator in self.validator_set:
            chain = utils.build_chain(
                validator.my_latest_message(),
                None
                )
            edgelist.append(utils.edge(chain, 2, 'blue', 'solid'))

        edgelist.append(utils.edge(self.blockchain, 2, 'grey', 'solid'))
        edgelist.append(utils.edge(self.communications, 1, 'black', 'dotted'))

        message_labels = {}
        for block in self.network.global_view.messages:
            message_labels[block] = block.sequence_number

        self.plot_tool.next_viewgraph(
            self.network.global_view,
            self.validator_set,
            edges=edgelist,
            message_colors=self.block_fault_tolerance,
            message_labels=message_labels
        )
