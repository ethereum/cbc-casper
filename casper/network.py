"""The network module contains a network class allowing for message passing """
import random as r
from utils.priority_queue import PriorityQueue
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol


class Network(object):
    """Simulates a network that allows for message passing between validators."""
    def __init__(self, validator_set, protocol=BlockchainProtocol, force_justify_messages=False):
        self.validator_set = validator_set
        self.global_view = protocol.View(
            self._collect_initial_messages(),
            protocol.initial_message(None)
        )
        self.message_queues = {
            validator: PriorityQueue()
            for validator in self.validator_set
        }
        self.time = 0

        self.force_justify_messages = force_justify_messages

    #
    # async network rework
    #
    def delay(self, sender, receiver):
        # return 1
        return r.choice([i for i in range(3)])

    def send(self, validator, message):
        self.global_view.add_messages(
            set([message])
        )
        self.message_queues[validator].put((
            self.time + self.delay(message.sender, validator),
            message
        ))

    def receive(self, validator):
        queue = self.message_queues[validator]
        if queue.qsize() == 0:
            return None
        if queue.peek()[0] > self.time:
            return None

        return queue.get()[1]

    def receive_all(self, validator):
        messages = []
        message = self.receive(validator)
        while message:
            messages.append(message)
            message = self.receive(validator)

        return messages

    def send_to_all(self, message):
        for validator in self.validator_set:
            if validator == message.sender:
                continue
            self.send(validator, message)

    #
    # legacy sync network
    #
    # def propagate_message_to_validator(self, message, validator):
        # """Propagate a message to a validator."""
        # assert message.hash in self.global_view.justified_messages, (
            # "...expected only to propagate messages "
            # "from the global view")
        # assert validator in self.validator_set, "...expected a known validator"

        # validator.receive_messages(set([message]))

        # HACK TO SEND ALL MESSAGES BEFORE NETWORK REWORK
        # if self.force_justify_messages:
            # self._propagate_messages_needed_to_justify(message, validator)

    # def get_message_from_validator(self, validator):
        # """Get a message from a validator."""
        # assert validator in self.validator_set, "...expected a known validator"

        # new_message = validator.make_new_message()
        # self.global_view.add_messages(set([new_message]))
        # assert new_message.hash in self.global_view.justified_messages

        # return new_message

    # def view_initialization(self, view):
        # """Initalizes all validators with all messages in some view."""
        # messages = view.justified_messages.values()

        # self.global_view.add_messages(messages)

        # for validator in self.validator_set:
            # validator.receive_messages(messages)

    def _collect_initial_messages(self):
        initial_messages = set()

        for validator in self.validator_set:
            initial_messages.update(validator.view.justified_messages.values())

        return initial_messages

    # def _propagate_messages_needed_to_justify(self, message, validator):
        # validator.receive_messages(self._messages_needed_to_justify(message, validator))
        # assert message.hash in validator.view.justified_messages

    # def _messages_needed_to_justify(self, message, validator):
        # messages_needed = set()

        # current_message_hashes = set()
        # for message_hash in message.justification.values():
            # if message_hash not in validator.view.pending_messages and \
               # message_hash not in validator.view.justified_messages:
                # current_message_hashes.add(message_hash)

        # while any(current_message_hashes):
            # next_hashes = set()

            # for message_hash in current_message_hashes:
                # current_message = self.global_view.justified_messages[message_hash]
                # messages_needed.add(current_message)

                # for other_hash in current_message.justification.values():
                    # if other_hash not in validator.view.pending_messages and \
                       # other_hash not in validator.view.justified_messages:
                        # next_hashes.add(other_hash)

            # current_message_hashes = next_hashes

        # return messages_needed
