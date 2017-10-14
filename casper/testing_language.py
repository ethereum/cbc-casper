"""The testing language module ... """
import re
import random as r

import casper.settings as s
from casper.network import Network
from casper.safety_oracles.clique_oracle import CliqueOracle
import casper.utils as utils


class TestLangCBC:
    """Allows testing of simulation scenarios with small testing language."""

    # Signal to py.test that TestLangCBC should not be discovered.
    __test__ = False

    TOKEN_PATTERN = '([A-Za-z]*)([0-9]*)([-]*)([A-Za-z0-9]*)'

    def __init__(self, test_string, val_weights, display=False):
        if test_string == '':
            raise Exception("Please pass in a valid test string")

        # Update the settings for this test.
        s.update(val_weights)

        self.test_string = test_string

        self.display = display

        self.network = Network()

        # This seems to be misnamed. Just generates starting blocks.
        self.network.random_initialization()

        self.blocks = dict()
        self.blockchain = []
        self.communications = []
        self.safe_blocks = set()
        self.color_mag = dict()

        # Register token handlers.
        self.handlers = dict()
        self.handlers['B'] = self.make_block
        self.handlers['S'] = self.send_block
        self.handlers['C'] = self.check_safety
        self.handlers['U'] = self.no_safety
        self.handlers['H'] = self.check_head_equals_block
        self.handlers['RR'] = self.round_robin
        self.handlers['R'] = self.report

    def send_block(self, validator, block_name):
        """Send some validator a block."""
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
        if block_name not in self.blocks:
            raise Exception('Block {} does not exist'.format(block_name))

        block = self.blocks[block_name]

        if block in self.network.validators[validator].view.messages:
            raise Exception(
                'Validator {} has already seen block {}'
                .format(validator, block_name)
            )

        self.network.propagate_message_to_validator(block, validator)

    def make_block(self, validator, block_name):
        """Have some validator produce a block."""
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
        if block_name in self.blocks:
            raise Exception('Block {} already exists'.format(block_name))

        new_block = self.network.get_message_from_validator(validator)

        if new_block.estimate is not None:
            self.blockchain.append([new_block, new_block.estimate])

        self.blocks[block_name] = new_block

    def round_robin(self, validator, block_name):
        """Have each validator create a block in a perfect round robin."""
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
        if block_name in self.blocks:
            raise Exception('Block {} already exists'.format(block_name))

        for i in range(s.NUM_VALIDATORS - 1):
            rand_name = r.random()
            self.make_block((validator + i) % s.NUM_VALIDATORS, rand_name)
            self.send_block((validator + i + 1) % s.NUM_VALIDATORS, rand_name)

        # Only the last block of the round robin is named.
        block_maker = (validator + s.NUM_VALIDATORS - 1) % s.NUM_VALIDATORS
        block_receiver = (validator + s.NUM_VALIDATORS) % s.NUM_VALIDATORS
        self.make_block(block_maker, block_name)
        self.send_block(block_receiver, block_name)

    def check_safety(self, validator, block_name):
        """Check that some validator detects safety on a block."""
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
        if block_name not in self.blocks:
            raise Exception('Block {} does not exist'.format(block_name))

        block = self.blocks[block_name]
        safe = self.network.validators[validator].check_estimate_safety(block)

        # NOTE: This may fail because the safety_oracle might be a lower bound,
        # so this might be better not as an assert :)
        assert safe, "Block {} failed safety assert".format(block_name)

    def no_safety(self, validator, block_name):
        """Check that some validator does not detect safety on a block."""
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
        if block_name not in self.blocks:
            raise Exception('Block {} does not exist'.format(block_name))

        block = self.blocks[block_name]

        safe = self.network.validators[validator].check_estimate_safety(block)

        # NOTE: Unlike above, this should never fail.
        # An oracle should, never detect safety when there is no safety.
        assert not safe, "Block {} failed no-safety assert".format(block_name)

    def check_head_equals_block(self, validator, block_name):
        """Check some validators forkchoice is the correct block."""
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
            # NOTE: Need to add special validator number to check the global forkchoice,
            # see issue #42 (same with safety and no safety).
        if block_name not in self.blocks:
            raise Exception('Block {} does not exist'.format(block_name))

        block = self.blocks[block_name]

        head = self.network.validators[validator].view.estimate()

        assert block == head, "Validator {} does not have block {} at head".format(validator, block_name)

    def parse(self):
        """Parse the test_string, and run the test"""
        for token in self.test_string.split(' '):
            letter, number, d, name = re.match(self.TOKEN_PATTERN, token).groups()
            if letter+number+d+name != token:
                raise Exception("Bad token: %s" % token)
            if number != '':
                number = int(number)

            self.handlers[letter](number, name)

    def report(self, num, name):
        """Display the view graph of the current global_view"""
        assert num == name and num == '', "...no validator or number needed to report!"

        if not self.display:
            return

        # Update the safe blocks!
        tip = self.network.global_view.estimate()
        while tip:
            if self.color_mag.get(tip, 0) == s.NUM_VALIDATORS - 1:
                break

            # Clique_Oracle used for display - change?
            oracle = CliqueOracle(tip, self.network.global_view)
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.safe_blocks.add(tip)
                self.color_mag[tip] = num_node_ft

            tip = tip.estimate

        edgelist = []

        best_chain = utils.build_chain(
            self.network.global_view.estimate(),
            None
        )
        edgelist.append(self._edge(best_chain, 5, 'red', 'solid'))

        for i in range(s.NUM_VALIDATORS):
            v = utils.build_chain(
                self.network.validators[i].my_latest_message(),
                None
                )
            edgelist.append(self._edge(v, 2, 'blue', 'solid'))

        edgelist.append(self._edge(self.blockchain, 2, 'grey', 'solid'))
        edgelist.append(self._edge(self.communications, 1, 'black', 'dotted'))

        self.network.report(
            colored_messages=self.safe_blocks,
            color_mag=self.color_mag,
            edges=edgelist
        )

    def _edge(self, edges, width, color, style):
        return {
            'edges': edges,
            'width': width,
            'edge_color': color,
            'style': style
        }
