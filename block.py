import copy
from settings import VALIDATOR_NAMES
from justification import Justification


class Block:
    def __eq__(self, block):
        if block is None:
            return False
        if isinstance(block, int):
            return False
        return self.sender == block.sender and self.estimate == block.estimate

    def __init__(self, estimate, justification, sender):
        # genesis block! 0

        assert sender in VALIDATOR_NAMES, "...expected a validator!"
        assert isinstance(estimate, Block) or estimate is None, "...expected a prevblock!"
        # assert isinstance(justification, Justification), "expected justification a Justification!"

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

    def __hash__(self):
        return hash(str(self.sequence_number + 10000*self.sender))

    def is_decendant(self, block):
        assert isinstance(block, Block), "...expected a block"

        if self == block:
            return True

        if block.sequence_number <= self.sequence_number:
            return False

        candidate = block.justification.latest_messages[block.sender]

        while(candidate.sequence_number > self.sequence_number):

            if candidate == self:
                return True

            candidate = candidate.estimate

        return False
