"""The Bet module implements the message data structure for integer consensus"""
from casper.message import Message


class Bet(Message):
    """Message data structure for integer consensus"""

    @classmethod
    def is_valid_estimate(cls, estimate):
        if not isinstance(estimate, int):
            return False
        return True

    def conflicts_with(self, message):
        """Returns true if the other_message estimate is not the same as this estimate"""
        assert isinstance(message.estimate, int), "... estimate should be an integer!"

        return self.estimate != message.estimate
