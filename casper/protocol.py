import re
import random
import string

from casper.validator_set import ValidatorSet

TOKEN_PATTERN = '([A-Za-z]*)([-]*)([0-9]*)([-]*)([A-Za-z0-9]*)([-]*)([(){A-Za-z0-9,}]*)'

class Protocol(object):

    def __init__(
            self,
            num_validators,
            execution_string,
            messages_per_round,
            display,
            save,
            plot_tool,
            view_cls,
            message_cls
        ):
        self.global_validator_set = ValidatorSet(num_validators, view_cls, message_cls)
        self.global_view = view_cls()

        self.plot_tool = plot_tool(display, save, self.global_view, self.global_validator_set)

        self.unexecuted = execution_string
        self.executed = ''

        self.messages_per_round = messages_per_round
        self.messages_this_round = 0

        self.messages = dict()
        self.message_from_hash = dict()
        self.message_name_from_hash = dict()

        self.handlers = dict()
        self.register_handler('M', self.make_message)
        self.register_handler('S', self.send_message)
        self.register_handler('SJ', self.send_and_justify)

    def register_handler(self, token, function):
        """Registers a function with a new token. Throws an error if already registered"""
        if token in self.handlers:
            raise KeyError('A function has been registered with that token')

        self.handlers[token] = function

    def register_message(self, message, name):
        """Save a message with a given name"""
        if name in self.messages:
            raise KeyError("Message with name {} already exists".format(name))
        if message.hash in self.message_from_hash:
            raise KeyError("Message with hash {} already exists".format(message.hash))

        self.messages[name] = message
        self.message_from_hash[message.hash] = message
        self.message_name_from_hash[message.hash] = name

        self.global_view.add_messages([message])
        self.plot_tool.update(new_messages=[message])

    def make_message(self, validator, message_name, data):
        """Have a validator generate a new message"""
        new_message = validator.make_new_message()
        self.register_message(new_message, message_name)

    def send_message(self, validator, message_name, data):
        """Send a message to a validator"""
        message = self.messages[message_name]
        validator.receive_messages(set([message]))

    def send_and_justify(self, validator, message_name, data):
        message = self.messages[message_name]
        messages_to_send = self._messages_needed_to_justify(message, validator)
        validator.receive_messages(messages_to_send)

    def _messages_needed_to_justify(self, message, validator):
        """Returns the set of messages needed to justify a message to a validator"""
        messages_needed = set([message])

        current_message_hashes = set()
        for message_hash in message.justification.values():
            if message_hash not in validator.view.justified_messages:
                current_message_hashes.add(message_hash)

        while any(current_message_hashes):
            next_hashes = set()

            for message_hash in current_message_hashes:
                message = self.message_from_hash[message_hash]
                messages_needed.add(message)

                for other_hash in message.justification.values():
                    if other_hash not in validator.view.justified_messages:
                        next_hashes.add(other_hash)

            current_message_hashes = next_hashes

        return messages_needed

    def execute(self, additional_str=None):
        if additional_str:
            self.unexecuted += additional_str

        for token in self.unexecuted.split():
            comm, vali, name, data = self.parse_token(token)

            validator = self.global_validator_set.get_validator_by_name(int(vali))
            self.handlers[comm](validator, name, data)

            if comm == 'M':
                self.messages_this_round += 1
                if self.messages_this_round % self.messages_per_round == 0:
                    self.plot_tool.plot()
                    self.messages_this_round = 0

        self.executed += self.unexecuted
        self.unexecuted = ''

        self.plot_tool.make_gif()

    def parse_token(self, token):
        comm, _, vali, _, name, _, data = re.match(
            TOKEN_PATTERN, token
        ).groups()

        if data:
            if comm + '-' + vali + '-' + name + '-' + data != token:
                raise ValueError("Bad token: {}".format(token))
        else:
            if comm + '-' + vali + '-' + name != token:
                raise ValueError("Bad token: {}".format(token))

        return comm, vali, name, data
