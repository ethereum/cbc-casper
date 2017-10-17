"""The testing language module ... """
import re
import random as r

from casper.network import Network
from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.validator_set import ValidatorSet
import casper.utils as utils


class TestLangCBC:
    """Allows testing of simulation scenarios with small testing language."""

    # Signal to py.test that TestLangCBC should not be discovered.
    __test__ = False

    TOKEN_PATTERN = '([A-Za-z]*)([0-9]*)([-]*)([A-Za-z0-9]*)'

    def __init__(self, test_string, val_weights, display=False):
        if test_string == '':
            raise Exception("Please pass in a valid test string")

        self.validator_set = ValidatorSet({i: w for i, w in enumerate(val_weights)})
        self.test_string = test_string
        self.display = display
        self.network = Network(self.validator_set)

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

    def _validate_validator(self, validator):
        if validator not in self.validator_set:
            raise ValueError('Validator {} does not exist'.format(validator))

    def _validate_block_exists(self, block_name):
        if block_name not in self.blocks:
            raise ValueError('Block {} does not exist'.format(block_name))

    def _validate_block_does_not_exist(self, block_name):
        if block_name in self.blocks:
            raise ValueError('Block {} already exists'.format(block_name))

    def parse(self):
        """Parse the test_string, and run the test"""
        for token in self.test_string.split(' '):
            letter, validator, dash, name = re.match(self.TOKEN_PATTERN, token).groups()
            if letter+validator+dash+name != token:
                raise ValueError("Bad token: %s" % token)
            if validator != '':
                try:
                    validator = self.validator_set.get_validator_by_name(int(validator))
                except KeyError:
                    raise ValueError("Validator {} does not exist".format(validator))

            self.handlers[letter](validator, name)

    def send_block(self, validator, block_name):
        """Send some validator a block."""
        self._validate_validator(validator)
        self._validate_block_exists(block_name)

        block = self.blocks[block_name]

        if block in validator.view.messages:
            raise Exception(
                'Validator {} has already seen block {}'
                .format(validator, block_name)
            )

        self.network.propagate_message_to_validator(block, validator)

    def make_block(self, validator, block_name):
        """Have some validator produce a block."""
        self._validate_validator(validator)
        self._validate_block_does_not_exist(block_name)

        new_block = self.network.get_message_from_validator(validator)

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
            self.send_block(receiver, name)

    def check_safety(self, validator, block_name):
        """Check that some validator detects safety on a block."""
        self._validate_validator(validator)
        self._validate_block_exists(block_name)

        block = self.blocks[block_name]
        safe = validator.check_estimate_safety(block)

        # NOTE: This may fail because the safety_oracle might be a lower bound,
        # so this might be better not as an assert :)
        assert safe, "Block {0} failed safety assert " \
                     "for validator-{1}".format(block_name, validator.name)

    def no_safety(self, validator, block_name):
        """Check that some validator does not detect safety on a block."""
        self._validate_validator(validator)
        self._validate_block_exists(block_name)

        block = self.blocks[block_name]

        safe = validator.check_estimate_safety(block)

        # NOTE: Unlike above, this should never fail.
        # An oracle should, never detect safety when there is no safety.
        assert not safe, "Block {} failed no-safety assert".format(block_name)

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
        while tip:
            if self.color_mag.get(tip, 0) == len(self.validator_set) - 1:
                break

            # Clique_Oracle used for display - change?
            oracle = CliqueOracle(tip, self.network.global_view, self.validator_set)
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

        for validator in self.validator_set:
            chain = utils.build_chain(
                validator.my_latest_message(),
                None
                )
            edgelist.append(self._edge(chain, 2, 'blue', 'solid'))

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
