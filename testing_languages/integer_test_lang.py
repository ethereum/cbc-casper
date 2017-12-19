"""The testing language module ... """
import re
import random as r

from simulations.state_language import StateLanguage
from casper.protocols.integer.integer_protocol import IntegerProtocol


class IntegerTestLang(StateLanguage):
    """Allows testing of simulation scenarios with small testing language."""

    # Signal to py.test that TestLangCBC should not be discovered.
    __test__ = False

    def __init__(self, val_weights, display=False):
        super().__init__(val_weights, IntegerProtocol, display)

    def check_estimate(self, validator, estimate):
        """Check that a validators estimate is the correct number"""
        estimate = int(estimate)

        num = validator.view.estimate()

        assert num == estimate, "Validator {} does not have " \
                              "estimate {}".format(validator, estimate)

    def check_safe(self, validator, estimate):
        """Check that some validator is safe on the correct integer."""
        estimate = int(estimate)

        validator.update_safe_estimates()

        assert validator.view.last_finalized_estimate is not None and \
            validator.view.last_finalized_estimate.estimate == estimate, \
            "{0} failed safety assert for validator-{1}".format(estimate, validator.name)

    def check_unsafe(self, validator, estimate):
        """Check that some validator is not safe on some integer."""
        estimate = int(estimate)

        validator.update_safe_estimates()

        assert validator.view.last_finalized_estimate is None or \
            validator.view.last_finalized_estimate.estimate != estimate, \
            "{0} failed no-safety assert for validator-{1}".format(estimate, validator)
