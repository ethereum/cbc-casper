"""The view module ... """
from casper.justification import Justification


class AbstractView(object):
    """A set of seen messages. For performance, also stores a dict of most recent messages."""
    def __init__(self, messages=None):
        # now for some assignment...
        if messages is None:
            messages = set()

        self.add_messages(messages)

        self.justified_messages = dict()            # message header => message
        self.pending_messages = dict()              # message header => message

        self.missing_message_dependencies = dict()  # message header => set(message headers)
        self.dependents_of_message = dict()         # message header => list(message headers)

        self.latest_messages = dict()


    def justification(self):
        """Returns the headers of latest message seen from other validators."""
        return Justification(self.latest_messages)

    def _next_sequence_number(self, validator):
        """Returns the sequence number for the next message from a validator"""
        if validator not in self.latest_messages:
            return 0

        return self.latest_messages[validator].sequence_number + 1

    def _next_display_height(self):
        """Returns the display height for a message created in this view"""
        if not any(self.latest_messages):
            return 0

        max_height = max(
            self.latest_messages[validator].display_height
            for validator in self.latest_messages
        )
        return max_height + 1


    def get_missing_messages_in_justification(self, message):
        """Returns the set of not seen messages headers from the justification of a message"""
        missing_message_headers = set()

        for message_header in message.justification.latest_messages.values():
            if message_header not in self.justified_messages:
                missing_message_headers.add(message_header)

        return missing_message_headers

    def add_messages(self, showed_messages):
        """Adds a set of newly recieved messages to pending or justified"""
        if not showed_messages:
            return

        for message in showed_messages:
            if message.header in self.pending_messages or message.header in self.justified_messages:
                continue

            missing_message_headers = self.get_missing_messages_in_justification(message)
            if not any(missing_message_headers):
                newly_justified_messages = {message}
                newly_justified_messages.update(self.resolve_waiting_messages(message))
                self.add_to_justified_messages(newly_justified_messages)

                for message_header in self.pending_messages:
                    assert message_header in self.missing_message_dependencies
            else:
                for missing_message_header in missing_message_headers:
                    if missing_message_header not in self.dependents_of_message:
                        self.dependents_of_message[missing_message_header] = []

                    self.dependents_of_message[missing_message_header].append(message.header)
                    self.missing_message_dependencies[message.header] = missing_message_headers
                    self.pending_messages[message.header] = message


    def resolve_waiting_messages(self, message):
        """Given a new message, resolve all messages that are waiting for it to be justified"""
        if message.header not in self.dependents_of_message:
            return set()

        newly_justified_messages = set()
        for message_header in self.dependents_of_message[message.header]:
            # sanity check!
            assert message.header in self.missing_message_dependencies[message_header]

            self.missing_message_dependencies[message_header].remove(message.header)

            if not any(self.missing_message_dependencies[message_header]):
                new_message = self.pending_messages[message_header]
                newly_justified_messages.add(new_message)
                newly_justified_messages.update(self.resolve_waiting_messages(new_message))
                del self.missing_message_dependencies[message_header]
                del self.pending_messages[message_header]

        del self.dependents_of_message[message.header]
        return newly_justified_messages

    def add_to_justified_messages(self, messages):
        """Must be defined in child class
        Adds a message with all messages in justification recieved to view"""

    def estimate(self):
        '''Must be defined in child class.
        Returns estimate based on current messages in the view'''
        pass

    def make_new_message(self, validator):
        '''Must be defined in child class.'''
        pass

    def update_safe_estimates(self, validator_set):
        '''Must be defined in child class.'''
        pass
