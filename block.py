import copy
import settings as s

from justification import Justification


class Block:
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

        assert sender in s.VALIDATOR_NAMES, "...expected a validator!"
        assert isinstance(estimate, Block) or estimate is None, "...expected a prevblock!"
        assert isinstance(justification, Justification), "expected justification a Justification!"

        # All other blocks!
        # ...then do some assignment
        self.sender = sender
        self.estimate = estimate
        self.justification = justification

        # the sequence number makes certain operations more efficient (like checking if bets are later)
        if self.sender not in self.justification.latest_messages:
            self.sequence_number = 0
        else:
            self.sequence_number = self.justification.latest_messages[self.sender].sequence_number + 1

        # the "heights" of bets are used for visualization of views
        if self.justification.is_null():
            self.height = 0
        else:
            candidate_max = 0
            for v in self.justification.latest_messages:
                if self.justification.latest_messages[v].height > candidate_max:
                    candidate_max = self.justification.latest_messages[v].height

            self.height = candidate_max + 1

        self.hash = self.__hash__()

    def __hash__(self):
        if self.estimate is None:
            return hash(str(self.sequence_number) + str(123123124124) + str(10000*self.sender))
        else:
            return hash(str(self.sequence_number) + str(self.estimate.hash) + str(10000*self.sender))

    def is_in_blockchain(self, block):
        assert isinstance(block, Block), "...expected a block"

        if self == block:
            return True

        if block.estimate is None:
            return False

        return self.is_in_blockchain(block.estimate)
