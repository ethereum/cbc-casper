"""The testing language module ... """
import re
import random as r

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.networks import NoDelayNetwork
from casper.validator_set import ValidatorSet


class StateLanguage(object):
    """Allows testing of simulation scenarios with small testing language."""

    TOKEN_PATTERN = '([A-Za-z]*)([0-9]*)([-]*)([A-Za-z0-9]*)([\\{A-Za-z,}]*)'

    def __init__(self, val_weights, protocol=BlockchainProtocol, display=False):

        self.validator_set = ValidatorSet(val_weights, protocol)
        self.network = NoDelayNetwork(self.validator_set, protocol)

        self.messages = dict()

        self.plot_tool = protocol.PlotTool(
            display,
            False,
            self.network.global_view,
            self.validator_set
        )

        # Register token handlers.
        self.handlers = dict()

        self.register_handler('M', self.make_message)
        self.register_handler('I', self.make_invalid)
        self.register_handler('S', self.send_message)
        self.register_handler('P', self.plot)
        self.register_handler('SJ', self.send_and_justify)
        self.register_handler('RR', self.round_robin)
        self.register_handler('CE', self.check_estimate)
        self.register_handler('CS', self.check_safe)
        self.register_handler('CU', self.check_unsafe)

    def register_handler(self, token, function):
        """Registers a function with a new token. Throws an error if already registered"""
        if token in self.handlers:
            raise KeyError('A function has been registered with that token')

        self.handlers[token] = function

    def make_message(self, validator, message_name, messages_to_hide=None):
        """Have a validator generate a new message"""
        self.require_message_not_exists(message_name)

        #NOTE: Once validators have the ability to lie about their view, hide messages_to_hide!

        new_message = validator.make_new_message()
        self.network.global_view.add_messages(
            set([new_message])
        )

        self.plot_tool.update([new_message])

        self.messages[message_name] = new_message

    def send_message(self, validator, message_name):
        """Send a message to a specific validator"""
        self.require_message_exists(message_name)

        message = self.messages[message_name]

        self._propagate_message_to_validator(validator, message)

    def make_invalid(self, validator, message_name):
        """TODO: Implement this when validators can make/handle invalid messages"""
        raise NotImplementedError

    def send_and_justify(self, validator, message_name):
        self.require_message_exists(message_name)

        message = self.messages[message_name]
        self._propagate_message_to_validator(validator, message)

        messages_to_send = self._messages_needed_to_justify(message, validator)
        for message in messages_to_send:
            self._propagate_message_to_validator(validator,  message)

        assert self.messages[message_name].hash in validator.view.justified_messages

    def round_robin(self, validator, message_name):
        """Have each validator create a message in a perfect round robin."""
        self.require_message_not_exists(message_name)

        # start round robin at validator specified by validator in args
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

    def plot(self):
        """Display or save a viewgraph"""
        self.plot_tool.plot()

    def check_estimate(self, validator, estimate):
        """Must be implemented by child class"""
        raise NotImplementedError

    def check_safe(self, validator, estimate):
        """Must be implemented by child class"""
        raise NotImplementedError

    def check_unsafe(self, validator, estimate):
        """Must be implemented by child class"""
        raise NotImplementedError

    def require_message_exists(self, message_name):
        """Throws an error if message_name does not exist"""
        if message_name not in self.messages:
            raise ValueError('Block {} does not exist'.format(message_name))

    def require_message_not_exists(self, message_name):
        """Throws an error if message_name does not exist"""
        if message_name in self.messages:
            raise ValueError('Block {} already exists'.format(message_name))

    def _propagate_message_to_validator(self, validator, message):
        self.network.send(validator, message)
        received_message = self.network.receive(validator)
        if received_message:
            validator.receive_messages(set([received_message]))

    def _messages_needed_to_justify(self, message, validator):
        """Returns the set of messages needed to justify a message to a validator"""
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

    def parse(self, protocol_state_string):
        """Parse the state string!"""
        for token in protocol_state_string.split():
            letter, validator, message = self.parse_token(token)

            if letter == 'P':
                self.plot()
            else:
                validator = self.validator_set.get_validator_by_name(int(validator))
                self.handlers[letter](validator, message)

    def parse_token(self, token):
        letter, validator, dash, message, removed_message_names = re.match(
            self.TOKEN_PATTERN, token
        ).groups()

        if letter + validator + dash + message + removed_message_names != token:
            raise ValueError("Bad token: %s" % token)

        return letter, validator, message
