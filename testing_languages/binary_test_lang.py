"""The testing language module ... """
import re
import random as r

from testing_languages.testing_language import TestingLanguage
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.networks import NoDelayNetwork
from casper.plot_tool import PlotTool
from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.validator_set import ValidatorSet
import casper.utils as utils


class BinaryTestLange(TestingLanguage):
    """Allows testing of simulation scenarios with small testing language."""

    # Signal to py.test that TestLangCBC should not be discovered.
    __test__ = False

    def __init__(self, val_weights, display=False):
        super().__init__(val_weights, BlockchainProtocol, display)

    def check_estimate(self, validator, estimate):
        """Check that a validators forkchoice is some block"""
        self.check_validator_exists(validator)
        self.check_message_exists(estimate)

        bit = validator.view.estimate()

        assert bit == estimate, "Validator {} does not have " \
                              "estimate {}".format(validator, estimate)

    def check_safe(self, validator, estimate):
        """Check that some validator does not detect safety on a block."""
        self.check_validator_exists(validator)
        self.check_message_exists(estimate)

        validator.update_safe_estimates()

        assert validator.view.last_finalized_estimate.estimate == estimate, \
            "{0} failed safety assert for validator-{1}".format(estimate, validator.name)

    def check_unsafe(self, validator, estimate):
        """Must be implemented by child class"""
        self.check_validator_exists(validator)
        self.check_message_exists(estimate)

        validator.update_safe_estimates()

        # NOTE: This should never fail
        assert validator.view.last_finalized_estimate is None or \
            validator.view.last_finalized_estimate.estimate != estimate, \
            "{0} failed no-safety assert for validator-{1}".format(estimate, validator)
