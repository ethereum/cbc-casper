"""The message module defines an abstract message class  """
import random as r
from casper.justification import Justification


class Message(object):
    """Message/bet data structure for blockchain consensus"""
    def __eq__(self, message):
        if message is None:
            return False
        return self.message_hash == message.message_hash

    def __ne__(self, message):
        return not self.__eq__(message)

    def __init__(self, estimate, justification, sender):
        assert isinstance(justification, Justification), "justification should be a Justification!"

        self.sender = sender
        self.estimate = estimate
        self.justification = justification

        if self.sender in self.justification.latest_messages:
            latest_message = self.justification.latest_messages[self.sender]
            self.sequence_number = latest_message.sequence_number + 1
        else:
            self.sequence_number = 0

        # The "display_height" of bets are used for visualization of views
        if not any(self.justification.latest_messages):
            self.display_height = 0
        else:
            max_height = max(
                self.justification.latest_messages[validator].display_height
                for validator in self.justification.latest_messages
            )
            self.display_height = max_height + 1

        self.message_hash = r.randint(0, 1000000)

    def __hash__(self):
        return hash(str(self.sender.name) + str(self.sequence_number) + str(self.message_hash))

    def conflicts_with(self, message):
        '''Must be implemented by child class'''
        pass
