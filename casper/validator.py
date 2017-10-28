"""The validator module ... """
import copy
import numbers
import random as r

from casper.blockchain.block import Block
from casper.blockchain.blockchain_view import BlockchainView
from casper.safety_oracles.clique_oracle import CliqueOracle

r.seed()
REPORT = True


class Validator(object):
    """A validator has a view from which it generates new messages and detects finalized blocks."""
    def __init__(self, name, weight, validator_set=None):
        if name is None:
            raise ValueError("Validator name must be defined.")
        if not isinstance(weight, numbers.Number):
            raise ValueError("Validator weight must a number.")
        if weight < 0:
            raise ValueError("Validator weight cannot be less than 0.")

        self.name = name
        self.weight = weight
        self.view = BlockchainView(set())
        self.validator_set = validator_set

    def receive_messages(self, messages):
        """Allows the validator to receive protocol messages."""
        self.view.add_messages(messages)

    def estimate(self):
        """The estimator function returns the set of max weight estimates.
        This may not be a single-element set because the validator may have an empty view."""
        return self.view.estimate()

    def my_latest_message(self):
        """This function returns the validator's latest message."""
        if self in self.view.latest_messages:
            return self.view.latest_messages[self]
        else:
            assert False

    def update_safe_estimates(self):
        """The validator checks estimate safety on some estimate with some safety oracle."""
        self.view.update_safe_estimates(self.validator_set)

    def make_new_message(self):
        """This function produces a new latest message for the validator.
        It updates the validator's latest message, estimate, view, and latest observed messages."""

        justification = self.view.justification()
        estimate = copy.copy(self.view.estimate())

        new_message = Block(estimate, justification, self)

        self.view.add_messages(set([new_message]))

        return new_message
