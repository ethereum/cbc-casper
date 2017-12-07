"""The network module contains a network class allowing for message passing """
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

    def delay(self, sender, receiver):
        '''Must be defined in child class.
        Returns delay of next message for sender to receiver'''
        raise NotImplementedError

    #
    # Validator API to Network
    #
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
    # helpers
    #
    def _collect_initial_messages(self):
        initial_messages = set()

        for validator in self.validator_set:
            initial_messages.update(validator.view.justified_messages.values())

        return initial_messages
