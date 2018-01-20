"""The block module implements the message data structure for a concurrent protocol"""
from casper.message import Message


class Block(Message):
    """Message data structure for concurrent consensus"""

    def __init__(self, estimate, justification, sender, sequence_number, display_height):
        # Do some type checking for safety!
        assert isinstance(estimate, dict), "...expected a valid estimate!"
        assert len(estimate['blocks']) > 0, "... most point to a least one thing"

        super().__init__(estimate, justification, sender, sequence_number, display_height)

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
