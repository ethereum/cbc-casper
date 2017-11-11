"""The view module ... """
from casper.justification import Justification


class AbstractView(object):
    """A set of seen messages. For performance, also stores a dict of most recent messages."""
    def __init__(self, messages=None):
        # now for some assignment...
        if messages is None:
            messages = set()

        self.add_messages(messages)

        self.justified_messages = dict() # message header => block

        self.messages_waiting_for = dict() # message header => list of message headers
        self.missing_dependencies_for = dict() # message header => set of message header
        self.pending_messages = dict() # message header => message

        self.latest_messages = dict()


    def justification(self):
        """Returns the latest messages seen from other validators, to justify estimate."""
        return Justification(self.latest_messages)

    def next_sequence_number(self, validator):
        """Returns the sequence number for the next message from a validator"""
        if validator not in self.latest_messages:
            return 0

        return self.latest_messages[validator].sequence_number + 1

    def next_display_height(self):
        """Returns the display height for a message created in this view"""
        if not any(self.latest_messages):
            return 0

        max_height = max(
            self.latest_messages[validator].display_height
            for validator in self.latest_messages
        )
        return max_height + 1


    def get_missing_messages_in_justification(self, message):
        """Returns any messages headers in the justification of a message not yet seen"""
        missing_message_headers = set()

        for message_header in message.justification.latest_messages:
            if message_header not in self.justified_messages:
                missing_message_headers.add(message_header)

        return missing_message_headers

    def add_messages(self, showed_messages):
        """Updates views latest_messages and children based on new messages"""
        if not showed_messages:
            return

        for message in showed_messages:
            missing_message_headers = self.get_missing_messages_in_justification(message)

            if not any(missing_message_headers):
                self.resolve_waiting_messages(message)
            else:
                for message_header in missing_message_headers:
                    if message_header not in self.messages_waiting_for:
                        self.messages_waiting_for[message_header] = []

                    self.messages_waiting_for[message_header].append(message.header)
                    self.missing_dependencies_for[message.header] = missing_message_headers

                self.resolve_waiting_messages(message)

    def resolve_waiting_messages(self, message):
        if message.header in self.messages_waiting_for:
            for message_header in self.messages_waiting_for:
                assert message.header in self.missing_dependencies_for[message_header]
                self.missing_dependencies_for[message_header].remove(message.header)

                if not any(self.missing_dependencies_for[message_header]):
                    del self.missing_dependencies_for[message_header]
                    self.add_to_justified_messages(self.pending_messages[message_header])
                    self.resolve_waiting_messages(self.justified_messages[message_header])

            del self.messages_waiting_for[message.header]
        else:
            self.add_to_justified_messages(message)


    def add_to_justified_messages(self, message):
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
