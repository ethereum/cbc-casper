"""The Bet module implements the message data structure for integer consensus"""
from casper.message import Message


class Bet(Message):
    """Message data structure for integer consensus"""

    def __init__(self, estimate, justification, sender):
        # Do some type checking for safety!
        assert isinstance(estimate, int), "... estimate should be an integer!"

        super().__init__(estimate, justification, sender)

    def conflicts_with(self, message):
        """Returns true if the other_message estimate is not the same as this estimate"""
        assert isinstance(message.estimate, int), "... estimate should be an integer!"

        return self.estimate != message.estimate
