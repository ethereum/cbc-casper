"""The validator module ... """
import copy
import numbers
import random as r

from casper.block import Block
from casper.view import View
from casper.safety_oracles.clique_oracle import CliqueOracle

r.seed()
REPORT = True


class Validator:
    """The validator's state is a function of its view and name alone (along w/ global variables).
    However, for performance's sake the validator also stores."""
    def __init__(self, name, weight):
        if name is None:
            raise ValueError("Validator name must be defined.")
        if not isinstance(weight, numbers.Number):
            raise ValueError("Validator weight must a number.")
        if weight < 0:
            raise ValueError("Validator weight cannot be less than 0.")

        self.name = name
        self.weight = weight
        self.view = View(set())

    def receive_messages(self, messages):
        """This method is the only way that a validator can receive protocol messages."""
        self.view.add_messages(messages)

    def estimate(self):
        """The estimator function returns the set of max weight estimates.
        This may not be a single-element set because the validator may have an empty view."""
        return self.view.estimate()

    def my_latest_message(self):
        """This function returns the validator's latest message."""
        if self.name in self.view.latest_messages:
            return self.view.latest_messages[self.name]
        else:
            assert False
            return None

    def check_estimate_safety(self, estimate):
        """The validator checks estimate safety by calling the safety oracle."""

        assert isinstance(estimate, Block), "..expected estimate to be a Block"

        oracle = CliqueOracle(estimate, self.view)
        fault_tolerance, _ = oracle.check_estimate_safety()

        if fault_tolerance > 0:
            if self.view.last_finalized_block:
                assert self.view.last_finalized_block.is_in_blockchain(estimate)

            self.view.last_finalized_block = estimate
            return True

        return False

    def make_new_message(self):
        """This function produces a new latest message for the validator.
        It updates the validator's latest message, estimate, view, and latest observed messages."""

        justification = self.view.justification()
        estimate = copy.copy(self.view.estimate())
        sender = self.name

        new_message = Block(estimate, justification, sender)

        self.view.add_messages(set([new_message]))

        return new_message
