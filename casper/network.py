"""The network module contains a network class allowing for message passing """
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol


class Network(object):
    """Simulates a network that allows for message passing between validators."""
    def __init__(self, validator_set, protocol=BlockchainProtocol, force_full_propagation=False):
        self.validator_set = validator_set
        initial_message = protocol.initial_message(None)
        val_initial_messages = self._collect_initial_messages()
        self.global_view = protocol.View(val_initial_messages, initial_message)
        self.force_full_propagation = force_full_propagation

    def propagate_message_to_validator(self, message, validator):
        """Propagate a message to a validator."""
        assert message.hash in self.global_view.justified_messages, (
            "...expected only to propagate messages "
            "from the global view")
        assert validator in self.validator_set, "...expected a known validator"

        validator.receive_messages(set([message]))

        # HACK TO SEND ALL MESSAGES BEFORE NETWORK REWORK
        if self.force_full_propagation:
            self._propagate_blocks_needed_to_justify(message, validator)

    def get_message_from_validator(self, validator):
        """Get a message from a validator."""
        assert validator in self.validator_set, "...expected a known validator"

        new_message = validator.make_new_message()
        self.global_view.add_messages(set([new_message]))
        assert new_message.hash in self.global_view.justified_messages

        return new_message

    def view_initialization(self, view):
        """Initalizes all validators with all messages in some view."""
        messages = view.justified_messages.values()

        self.global_view.add_messages(messages)

        for validator in self.validator_set:
            validator.receive_messages(messages)

    def _collect_initial_messages(self):
        initial_messages = set()

        for validator in self.validator_set:
            initial_messages.update(validator.view.justified_messages.values())

        return initial_messages

    def _propagate_blocks_needed_to_justify(self, message, validator):
        validator.receive_messages(self._messages_needed_to_justify(message, validator))
        assert message.hash in validator.view.justified_messages

    def _messages_needed_to_justify(self, message, validator):
        messages_needed = set()

        current_message_hashes = set()
        for message_hash in message.justification.values():
            if message_hash not in validator.view.pending_messages and \
               message_hash not in validator.view.justified_messages:
                current_message_hashes.add(message_hash)

        while any(current_message_hashes):
            next_hashes = set()

            for message_hash in current_message_hashes:
                current_message = self.global_view.justified_messages[message_hash]
                messages_needed.add(current_message)

                for other_hash in current_message.justification.values():
                    if other_hash not in validator.view.pending_messages and \
                       other_hash not in validator.view.justified_messages:
                        next_hashes.add(other_hash)

            current_message_hashes = next_hashes

        return messages_needed
