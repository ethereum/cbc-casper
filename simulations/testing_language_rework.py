"""The testing language module ... """
import re
import random as r

from simulations.state_language import StateLanguage
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.networks import NoDelayNetwork
from casper.plot_tool import PlotTool
from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.validator_set import ValidatorSet
import casper.utils as utils

class TestingLanguage(StateLanguage):
    """Test the blockchain!"""

    # Signal to py.test that TestingLanguage should not be discovered.
    __test__ = False

    def __init__(self, val_weights, protocol=BlockchainProtocol, display=False):
        super().__init__(val_weights, protocol, display)

        self.handlers['SJ'] = self.send_and_justify
        self.handlers['RR'] = self.round_robin

        self.handlers['CE'] = self.check_estimate
        self.handlers['CS'] = self.check_safe
        self.handlers['CU'] = self.check_unsafe

    def send_and_justify(self, message_name, validator):
        self.check_validator_exists(validator)
        self.check_message_exists(message_name)

        #TODO: This should use the send_message function!
        message = self.messages[message_name]
        self.propagate_message_to_validator(message, validator)

        messages_to_send = self._message_needed_to_justify(message, validator)
        for message in messages_to_send:
            self.propagate_message_to_validator(message, validator)

        assert self.messages[message_name].hash in validator.view.justified_messages

    def round_robin(self, validator, message_name):
        """Have each validator create a message in a perfect round robin."""
        self.check_validator_exists(validator)
        self.check_message_exists(message_name)

        # start round robin at validator speicied by validator in args
        validators = self.validator_set.sorted_by_name()
        start_index = validators.index(validator)
        validators = validators[start_index:] + validators[:start_index]

        for i in range(len(self.validator_set)):
            if i == len(self.validator_set) - 1:
                name = message_name
            else:
                name = r.random()
            maker = validators[i]
            receiver = validators[(i + 1) % len(validators)]

            self.make_message(maker, name)
            self.send_and_justify(receiver, name)


    def parse(self, test_string):
        """Parse the test_string, and run the test"""
        for token in test_string.split(' '):
            letter, validator, dash, message, removed_message_names = re.match(
                self.TOKEN_PATTERN, token
            ).groups()

            if letter + validator + dash + message + removed_message_names != token:
                raise ValueError("Bad token: %s" % token)

            if letter in ['M', 'I', 'S']:
                super.parse(token)
            elif letter == 'P':
                self.plot()
            else:
                validator = self.validator_set.get_validator_by_name(int(validator))
                self.handlers[letter](validator, message)


    def _message_needed_to_justify(self, message, validator):
        messages_needed = set()

        current_message_hashes = set()
        for message_hash in message.justification.values():
            if message_hash not in validator.view.pending_messages and \
               message_hash not in validator.view.justified_messages:
                current_message_hashes.add(message_hash)

        while any(current_message_hashes):
            next_hashes = set()

            for message_hash in current_message_hashes:
                message = self.network.global_view.justified_messages[message_hash]
                messages_needed.add(message)

                for other_hash in message.justification.values():
                    if other_hash not in validator.view.pending_messages and \
                       other_hash not in validator.view.justified_messages:
                        next_hashes.add(other_hash)

            current_message_hashes = next_hashes

        return messages_needed

    def check_estimate(self, validator, estimate):
        """Must be implemented by child class"""
        raise NotImplementedError

    def check_safe(self, validator, estimate):
        """Must be implemented by child class"""
        raise NotImplementedError

    def check_unsafe(self, validator, estimate):
        """Must be implemented by child class"""
        raise NotImplementedError
