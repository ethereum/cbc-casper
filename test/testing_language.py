import re
import random as r

import settings as s
from network import Network
from safety_oracles.clique_oracle import CliqueOracle
import utils
import plot_tool

class TestLangCBC:
    def __init__(self, test_string, val_weights):
        if test_string == '':
            raise Exception("Please pass in a valid test string")

        s.update(val_weights) # update the settings for this test

        self.test_string = test_string

        self.network = Network()
        self.network.random_initialization() # this seems to be misnamed. Just generates starting blocks.

        self.blocks = dict()
        self.blockchain = []
        self.communications = []
        self.safe_blocks = set()
        self.color_mag = dict()

        # Register token handlers
        self.handlers = dict()
        self.handlers['B'] = self.make_block
        self.handlers['S'] = self.send_block
        self.handlers['C'] = self.check_safety
        self.handlers['U'] = self.no_safety
        self.handlers['H'] = self.check_head_equals_block
        self.handlers['RR'] = self.round_robin
        self.handlers['R'] = self.report


    def send_block (self, validator, block_name):
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
        if block_name not in self.blocks:
            raise Exception('Block {} does not exist'.format(block_name))

        block = self.blocks[block_name]

        if block in self.network.validators[validator].view.messages:
            raise Exception('Validator {} has already seen block {}'.format(validator, block_name))

        self.network.propagate_message_to_validator(block, validator)


    def make_block(self, validator, block_name):
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
        if block_name in self.blocks:
             raise Exception('Block {} already exists'.format(block_name))

        new_block = self.network.get_message_from_validator(validator)

        if new_block.estimate is not None:
            self.blockchain.append([new_block, new_block.estimate])

        self.blocks[block_name] = new_block
        self.network.global_view.add_messages(set([new_block]))


    def round_robin(self, validator, block_name):
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
        if block_name in self.blocks:
             raise Exception('Block {} already exists'.format(block_name))

        for i in xrange(s.NUM_VALIDATORS - 1):
            rand_name = r.random()
            self.make_block((validator + i) % s.NUM_VALIDATORS, rand_name)
            self.send_block((validator + i + 1) % s.NUM_VALIDATORS, rand_name)

        # only the last block of the round robin is named
        self.make_block((validator + s.NUM_VALIDATORS - 1) % s.NUM_VALIDATORS, block_name)
        self.send_block((validator + s.NUM_VALIDATORS - 1 + 1) % s.NUM_VALIDATORS, block_name)


    def check_safety(self, validator, block_name):
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
        if block_name not in self.blocks:
            raise Exception('Block {} does not exist'.format(block_name))

        block = self.blocks[block_name]
        safe = self.network.validators[validator].check_estimate_safety(block)

        # NOTE: This may fail because the safety_oracle might be a lower bound,
        # so this be better not as an assert :)
        assert safe, "Block {} did not pass assert for safety".format(block_name)



    def no_safety(self, validator, block_name):
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
        if block_name not in self.blocks:
            raise Exception('Block {} does not exist'.format(block_name))

        block = self.blocks[block_name]

        safe = self.network.validators[validator].check_estimate_safety(block)

        # NOTE: Unlike above, this should never fail. An oracle should, never detect
        # safety when there is no safety
        assert not safe, "Block {} did not pass assert for no safety".format(block_name)



    def check_head_equals_block(self, validator, block_name):
        if validator not in self.network.validators:
            raise Exception('Validator {} does not exist'.format(validator))
            # TODO: add special validator number to check the global forkchoice
            # same with safety and no safety
        if block_name not in self.blocks:
            raise Exception('Block {} does not exist'.format(block_name))

        block = self.blocks[block_name]

        head = self.network.validators[validator].view.estimate()

        assert block == head, "Validator {} does not have block {} at head".format(validator, block_name)


    def parse(self):
        for token in self.test_string.split(' '):
            letter, number, d, name = re.match('([A-Za-z]*)([0-9]*)([-]*)([A-Za-z0-9]*)', token).groups()
            if letter+number+d+name != token:
                raise Exception("Bad token: %s" % token)
            if number != '':
                number = int(number)

            self.handlers[letter](number, name)


    def report(self, num, name):
        assert num == name and num == '', "...no validator or number needed to report!"

        # update the safe blocks!
        tip = self.network.global_view.estimate()
        while tip:
            if self.color_mag.get(tip, 0) == s.NUM_VALIDATORS - 1:
                break

            oracle = CliqueOracle(tip, self.network.global_view) # Clique_Oracle used for display - change?
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.safe_blocks.add(tip)
                self.color_mag[tip] = num_node_ft

            tip = tip.estimate

        edgelist = []

        best_chain = utils.build_chain(self.network.global_view.estimate(), None)
        edgelist.append({'edges':best_chain, 'width':5,'edge_color':'red','style':'solid'})

        for i in xrange(s.NUM_VALIDATORS):
            v = utils.build_chain(self.network.validators[i].my_latest_message(), None)
            edgelist.append({'edges':v,'width':2,'edge_color':'blue','style':'solid'})

        edgelist.append({'edges':self.blockchain, 'width':2,'edge_color':'grey','style':'solid'})
        edgelist.append({'edges':self.communications, 'width':1,'edge_color':'black','style':'dotted'})

        self.network.report(colored_messages=self.safe_blocks, color_mag=self.color_mag, edges=edgelist)
