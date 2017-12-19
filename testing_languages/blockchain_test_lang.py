"""The testing language module ... """
import re
import random as r

from simulations.state_language import StateLanguage
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol


class BlockchainTestLang(StateLanguage):
    """Allows testing of simulation scenarios with small testing language."""

    # Signal to py.test that TestLangCBC should not be discovered.
    __test__ = False

    def __init__(self, val_weights, display=False):
        super().__init__(val_weights, BlockchainProtocol, display)

    def check_estimate(self, validator, estimate):
        """Check that a validators forkchoice is some block"""
        self.check_message_exists(estimate)

        message = self.messages[estimate]

        head = validator.view.estimate()

        assert message == head, "Validator {} does not have " \
                              "block {} at head".format(validator.name, estimate)

    def check_safe(self, validator, estimate):
        """Check that some validator does not detect safety on a block."""
        self.check_message_exists(estimate)

        message = self.messages[estimate]
        validator.update_safe_estimates()

        # NOTE: This should never fail
        assert validator.view.last_finalized_block is None or \
            not message.conflicts_with(validator.view.last_finalized_block), \
            "Block {0} failed safety assert for validator-{1}".format(estimate, validator.name)

    def check_unsafe(self, validator, estimate):
        """Must be implemented by child class"""
        self.check_message_exists(estimate)

        message = self.messages[estimate]
        validator.update_safe_estimates()

        # NOTE: This should never fail
        assert validator.view.last_finalized_block is None or \
            message.conflicts_with(validator.view.last_finalized_block), \
            "Block {} failed no-safety assert".format(estimate)
