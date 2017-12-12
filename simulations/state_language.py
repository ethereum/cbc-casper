"""The testing language module ... """
import re

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.networks import NoDelayNetwork
from casper.validator_set import ValidatorSet


class StateLanguage(object):
    """Allows testing of simulation scenarios with small testing language."""

    # Signal to py.test that TestLangCBC should not be discovered.
    __test__ = False

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

        self.handlers['M'] = self.make_message
        self.handlers['I'] = self.make_invalid
        self.handlers['S'] = self.send_message

        self.handlers['P'] = self.plot


    def make_message(self, validator, message_name, messages_to_hide=None):
        self.check_validator_exists(validator)
        self.check_message_not_exists(message_name)

        if not messages_to_hide:
            messages_to_hide = set()

        #TODO: Once validators have the ability to lie about their view, hide messages!
        new_message = validator.make_new_message()
        self.network.global_view.add_messages(
            set([new_message])
        )

        self.plot_tool.update([new_message])

        self.messages[message_name] = new_message

    def send_message(self, validator, message_name):
        self.check_validator_exists(validator)
        self.check_message_exists(message_name)

        message = self.messages[message_name]

        self.propagate_message_to_validator(validator, message)


    def make_invalid(self, validator, message_name):
        """TODO: Implement this when validators can make/handle invalid messages"""
        raise NotImplementedError

    def check_validator_exists(self, validator):
        if validator not in self.validator_set:
            raise ValueError('Validator {} does not exist'.format(validator))

    def check_message_exists(self, message_name):
        if message_name not in self.messages:
            raise ValueError('Block {} does not exist'.format(message_name))

    def check_message_not_exists(self, message_name):
        if message_name in self.messages:
            raise ValueError('Block {} already exists'.format(message_name))

    def propagate_message_to_validator(self, validator, message):
        self.network.send(validator, message)
        received_message = self.network.receive(validator)
        if received_message:
            validator.receive_messages(set([received_message]))

    def plot(self):
        self.plot_tool.plot()

    def parse(self, protocol_state_string):
        """Parse the state string!"""
        for token in protocol_state_string.split(' '):
            letter, validator, dash, message, removed_message_names = re.match(
                self.TOKEN_PATTERN, token
            ).groups()

            if letter + validator + dash + message + removed_message_names != token:
                raise ValueError("Bad token: %s" % token)

            validator = self.validator_set.get_validator_by_name(int(validator))

            if letter == 'M':
                #TODO: parse removed_message_names in this case!
                removed_message = set()
                print("Validator: " + str(validator))
                self.handlers[letter](validator, message, removed_message)
            elif letter == 'P':
                self.handlers[letter]()
            else:
                self.handlers[letter](validator, message)
