"""The block module ... """
from casper.justification import Justification


class Block:
    """Message/bet data structure for blockchain consensus"""
    def __eq__(self, block):
        if block is None:
            return False
        if isinstance(block, int):
            return False
        return self.hash == block.hash

    def __ne__(self, block):
        return not self.__eq__(block)

    def __init__(self, estimate, justification, sender):
        # genesis block! 0

        # TODO: assert block created by a validator defined by the validator_set
        #       in the estimate once validator_set is part of Block (message)
        assert isinstance(estimate, Block) or estimate is None, "...expected a prevblock!"
        assert isinstance(justification, Justification), "expected justification a Justification!"

        # All other blocks!
        # ...then do some assignment
        self.sender = sender
        self.estimate = estimate
        self.justification = justification

        # The sequence number makes certain operations more
        # efficient (like checking if bets are later).
        if self.sender not in self.justification.latest_messages:
            self.sequence_number = 0
        else:
            self.sequence_number = self.justification.latest_messages[self.sender].sequence_number + 1

        # The "heights" of bets are used for visualization of views.
        if not any(self.justification.latest_messages):
            self.display_height = 0
        else:
            max_height = max(self.justification.latest_messages[validator].display_height \
                            for validator in self.justification.latest_messages)

            self.display_height = max_height + 1

        self.hash = self.__hash__()

    def __hash__(self):
        if self.estimate is None:
            return hash(str(self.sequence_number) + str(123123124124) + str(self.sender.name))
        else:
            return hash(str(self.sequence_number) + str(self.estimate.hash) + str(self.sender.name))

    def is_in_blockchain(self, block):
        """Returns True if self is an ancestor of block."""
        assert isinstance(block, Block), "...expected a block"

        if self == block:
            return True

        if block.estimate is None:
            return False

        return self.is_in_blockchain(block.estimate)
