import settings as s
from block import Block
from view import View
from justification import Justification
import copy

import random as r
r.seed()

REPORT = True


class Validator:

    # The validator's state is a function of its view and name alone (along with global variables)
    # However, for performance's sake the validator also stores
    def __init__(self, name):
        assert name in s.VALIDATOR_NAMES, "expected a validator name"
        self.name = name
        self.view = View(set())

    # This method is the only way that a validator can receive protocol messages
    def receive_messages(self, messages):
        self.view.add_messages(messages)

    # The estimator function returns the set of max weight estimates
    # This may not be a single-element set because the validator may have an empty view
    def estimate(self):
        return self.view.estimate()

    # This function returns the validator's latest message
    def my_latest_message(self):
        if self.name in self.view.latest_messages:
            return self.view.latest_messages[self.name]
        else:
            assert False
            return None

    # The validator checks estimate safety by calling the safety oracle
    def check_estimate_safety(self, estimate):

        assert isinstance(estimate, Block), "..expected estimate to be a Block"

        oracle = Safety_Oracle(estimate, self.view)
        fault_tolerance, min_node_ft = oracle.check_estimate_safety()

        if fault_tolerance > 0:
            if self.view.last_finalized_block is not None:
                assert self.view.last_finalized_block.is_in_blockchain(estimate)

            self.view.last_finalized_block = estimate
            return True

        return False

    # This function produces a new latest message for the validator
    # It updates the validator's latest message, estimate, view, and latest observed messages
    def make_new_message(self):

        justification = self.view.justification()
        estimate = copy.copy(self.view.estimate())
        sender = self.name

        new_message = Block(estimate, justification, sender)

        self.view.add_messages(set([new_message]))

        return new_message
