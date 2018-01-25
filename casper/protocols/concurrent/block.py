"""The block module implements the message data structure for a concurrent protocol"""
from casper.message import Message


class Block(Message):
    """Message data structure for concurrent consensus"""

    @classmethod
    def is_valid_estimate(cls, estimate):
        if not isinstance(estimate, dict):
            return False

        for field in ['blocks', 'inputs', 'outputs']:
            if field not in estimate:
                return False

        if len(estimate) != 3:
            return False

        if not isinstance(estimate['blocks'], set) or len(estimate['blocks']) < 1:
            return False

        return True

    def conflicts_with(self, message):
        """Returns true if self is not in the prev blocks of other_message"""
        assert isinstance(message, Block), "...expected a block"

        return not self.is_in_history(message)

    def is_in_history(self, block):
        """Returns True if self is an ancestor of block."""
        assert isinstance(block, Block), "...should be block, is"

        if self == block:
            return True

        if len(block.estimate['blocks']) == 1:
            for b in block.estimate['blocks']:
                if b is None:
                    return False

        for b in block.estimate['blocks']:
            # memoize in future for efficiency
            if self.is_in_history(b):
                return True

        return False
