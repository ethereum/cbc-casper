import copy
from settings import VALIDATOR_NAMES


class Block:
    def __eq__(self, block):
        if self.sender != block.sender:
            return False
        if self.estimate != block.estimate:
            return False
        if self.sequence_number != block.sequence_number:
            return False

        return True

    def __init__(self, estimate=0, justification=0, sender=0):
        # genesis block! 0

        if isinstance(estimate, int):
            self.sender = None
            self.estimate = None
            self.justification = None
            self.sequence_number = 0
            self.height = 0
            return

        assert sender in VALIDATOR_NAMES, "...expected a validator!"
        assert isinstance(estimate, Block), "...expected a prevblock!"
        # assert isinstance(justification, Justification), "expected justification a Justification!"

        # All other blocks!
        # ...then do some assignment
        self.sender = sender
        self.estimate = estimate
        self.justification = copy.copy(justification)

        # the sequence number makes certain operations more efficient (like checking if bets are later)
        if self.sender not in self.justification.latest_messages:
            self.sequence_number = 1
        else:
            self.sequence_number = self.justification.latest_messages[self.sender].sequence_number + 1

        # the "heights" of bets are used for visualization of views
        if self.justification.is_null():
            self.height = 1
        else:
            candidate_max = 1
            for v in self.justification.latest_messages:
                if self.justification.latest_messages[v].height > candidate_max:
                    candidate_max = self.justification.latest_messages[v].height

            self.height = candidate_max + 1

    def __hash__(self):
        if self.sender is None:
            return hash(0)
        return hash(self.sequence_number + self.sender)

    def is_decendant(self, block):
        assert isinstance(block, Block), "...expected a block"

        if self == block:
            return True

        if block.sequence_number <= self.sequence_number:
            return False

        sequence_number = block.sequence_number
        candidate = block.justification.latest_messages[block.sender]

        while(sequence_number > self.sequence_number):

            if candidate == self:
                return True

            candidate = candidate.justification.latest_messages[block.sender]
            sequence_number -= 1

        return False
