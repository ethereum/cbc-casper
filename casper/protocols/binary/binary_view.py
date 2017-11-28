"""The binary view module extends a view for binary data structures """
from casper.protocols.binary.bet import Bet
from casper.protocols.integer.integer_view import IntegerView


class BinaryView(IntegerView):
    """A view class that also keeps track of a last_finalized_block and children"""
    def __init__(self, messages=None):
        super().__init__(messages)

        self.minimum = 0
        self.maximum = 1
