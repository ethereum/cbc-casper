"""The testing language module ... """
import string
import random as r

from simulations.state_language import StateLanguage
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol

class TestingLanguage(StateLanguage):
    """Test the blockchain!"""

    # Signal to py.test that TestingLanguage should not be discovered.
    __test__ = False

    def __init__(self, val_weights, protocol=BlockchainProtocol, display=False):
        super().__init__(val_weights, protocol, display)

        self.handlers['CE'] = self.check_estimate
        self.handlers['CS'] = self.check_safe
        self.handlers['CU'] = self.check_unsafe

    def parse(self, protocol_state_string):
        """Parse the test_string, and run the test"""
        for token in protocol_state_string.split(' '):
            letter, validator_name, message_name = self.parse_token(token)

            if letter == 'SJ':
                token = self._translate_send_justified(validator_name, message_name)
            if letter == 'RR':
                token = self._translate_round_robin(validator_name, message_name)

            super().parse(token)

    def _translate_send_justified(self, validator_name, message_name):
        translated_token = ''
        validator = self.validator_set.get_validator_by_name(int(validator_name))

        message = self.messages[message_name]
        messages_to_send = self._message_names_needed_to_justify(message, validator)
        messages_to_send.append(message_name)

        for m_name in messages_to_send:
            translated_token += 'S' + validator_name + '-' + m_name + ' '

        return translated_token[:-1]

    def _translate_round_robin(self, validator_name, message_name):
        translated_token = ''
        validator = self.validator_set.get_validator_by_name(int(validator_name))

        # start round robin at validator specified by validator in args
        validators = self.validator_set.sorted_by_name()
        start_index = validators.index(validator)
        validators = validators[start_index:] + validators[:start_index]

        for i in range(len(self.validator_set)):
            if i == len(self.validator_set) - 1:
                name = message_name
            else:
                name = self._get_random_message_name()
            maker = validators[i]
            receiver = validators[(i + 1) % len(validators)]

            translated_token += 'M' + str(maker.name) + '-' + name + ' '
            translated_token += 'S' + str(receiver.name) + '-' + name + ' '

        return translated_token[:-1]

    def _get_random_message_name(self):
        random_name = ''.join([r.choice(string.ascii_letters) for n in range(10)])
        return random_name

    def _message_names_needed_to_justify(self, message, validator):
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

        return [self.message_names[message] for message in messages_needed]

    def check_estimate(self, validator, estimate):
        """Must be implemented by child class"""
        raise NotImplementedError

    def check_safe(self, validator, estimate):
        """Must be implemented by child class"""
        raise NotImplementedError

    def check_unsafe(self, validator, estimate):
        """Must be implemented by child class"""
        raise NotImplementedError
