from settings import ESTIMATE_SPACE, WEIGHTS
import random as r
from block import Block
import forkchoice


class Justification:
    def __init__(self, latest_messages=dict(), last_finalized_block=Block(), children=dict()):
        self.last_finalized_block = last_finalized_block
        self.latest_messages = latest_messages
        self.children = children

    def is_null(self):
        return self.latest_messages == dict()

    def estimate(self, default=None):
        return forkchoice.get_fork_choice(self.last_finalized_block, self.latest_messages, self.children)
