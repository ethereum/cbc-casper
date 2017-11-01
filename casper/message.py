"""The message module ... """
from casper.justification import Justification

class Message(object):
    """Message/bet data structure for blockchain consensus"""
    def __eq__(self, message):
        if message is None:
            return False
        return self.hash == message.hash

    def __ne__(self, message):
        return not self.__eq__(message)

    def __init__(self, estimate, justification, sender):
        assert isinstance(justification, Justification), "expected justification a Justification!"

        # set the necessary variables
        self.sender = sender
        self.estimate = estimate
        self.justification = justification

        # The sequence number makes certain operations more
        # efficient (like checking if bets are later).
        if self.sender not in self.justification.latest_messages:
            self.sequence_number = 0
        else:
            latest_message = self.justification.latest_messages[self.sender]
            self.sequence_number = latest_message.sequence_number + 1

        # The "display_height" of bets are used for visualization of views
        if not any(self.justification.latest_messages):
            self.display_height = 0
        else:
            max_height = max(self.justification.latest_messages[validator].display_height \
                            for validator in self.justification.latest_messages)

            self.display_height = max_height + 1

        self.hash = self.__hash__()

    def __hash__(self):
        # NOTE: This does not work once validators have the ability to equivocate!
        return hash(str(self.sequence_number) + str(123123124124) + str(self.sender.name))

    def conflicts_with(self, message):
        '''Must be implemented by child class'''
        pass
