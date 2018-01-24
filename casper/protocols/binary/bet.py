"""The Bet module implements the message data structure for binary consensus"""
from casper.message import Message


class Bet(Message):
    """Message data structure for binary consensus"""

    @classmethod
    def is_valid_estimate(cls, estimate):
        return estimate in [0, 1]

    def conflicts_with(self, message):
        """Returns true if the other_message estimate is not the same as this estimate"""
        assert message.estimate in {0, 1}, "... estimate should be binary!"

        return self.estimate != message.estimate
