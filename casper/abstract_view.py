"""The view module ... """


class AbstractView(object):
    """A set of seen messages. For performance, also stores a dict of most recent messages."""
    def __init__(self, messages=None):
        # now for some assignment...
        if messages is None:
            messages = set()

        self.add_messages(messages)

        self.justified_messages = dict()            # message hash => message
        self.pending_messages = dict()              # message hash => message

        self.num_missing_dependencies = dict()  # message hash => number of message hashes
        self.dependents_of_message = dict()         # message hash => list(message hashes)

        self.latest_messages = dict()               # validator => message

    def estimate(self):
        '''Must be defined in child class.
        Returns estimate based on current messages in the view'''
        raise NotImplementedError

    def update_safe_estimates(self, validator_set):
        '''Must be defined in child class.'''
        raise NotImplementedError

    def add_messages(self, showed_messages):
        """Adds a set of newly received messages to pending or justified"""
        for message in showed_messages:
            if message.hash in self.pending_messages or message.hash in self.justified_messages:
                continue

            missing_message_hashes = self._missing_messages_in_justification(message)
            if not any(missing_message_hashes):
                self.receive_justified_message(message)
            else:
                self.receive_pending_message(message, missing_message_hashes)

    def receive_justified_message(self, message):
        """Upon receiving a justified message, resolves waiting messages and adds to view"""
        newly_justified_messages = self.get_newly_justified_messages(message)

        for justified_message in newly_justified_messages:
            self._add_to_latest_messages(justified_message)
            self._add_justified_remove_pending(justified_message)
            self.update_protocol_specific_view(justified_message)

    def receive_pending_message(self, message, missing_message_hashes):
        """Updates and stores pending messages and dependencies"""
        self.pending_messages[message.hash] = message
        self.num_missing_dependencies[message.hash] = len(missing_message_hashes)

        for missing_message_hash in missing_message_hashes:
            if missing_message_hash not in self.dependents_of_message:
                self.dependents_of_message[missing_message_hash] = []

            self.dependents_of_message[missing_message_hash].append(message.hash)

    def update_protocol_specific_view(self, message):
        """ Can be implemented by child, though not necessary
        Updates a view's specific info, given a justified message"""
        pass

    def get_newly_justified_messages(self, message):
        """Given a new justified message, get all messages that are now justified
        due to its receipt"""
        newly_justified_messages = set([message])

        for dependent_hash in self.dependents_of_message.get(message.hash, set()):
            self.num_missing_dependencies[dependent_hash] -= 1

            if self.num_missing_dependencies[dependent_hash] == 0:
                new_message = self.pending_messages[dependent_hash]
                newly_justified_messages.update(self.get_newly_justified_messages(new_message))

        return newly_justified_messages

    def _add_to_latest_messages(self, message):
        """Updates a views most recent messages, if this message is later"""
        if message.sender not in self.latest_messages:
            self.latest_messages[message.sender] = message
        elif self.latest_messages[message.sender].sequence_number < message.sequence_number:
            self.latest_messages[message.sender] = message

    def _add_justified_remove_pending(self, message):
        self.justified_messages[message.hash] = message
        if message.hash in self.num_missing_dependencies:
            del self.num_missing_dependencies[message.hash]
        if message.hash in self.dependents_of_message:
            del self.dependents_of_message[message.hash]
        if message.hash in self.pending_messages:
            del self.pending_messages[message.hash]

    def _missing_messages_in_justification(self, message):
        """Returns the set of not seen messages hashes from the justification of a message"""
        return {
            message_hash for message_hash in message.justification.values()
            if message_hash not in self.justified_messages
        }
