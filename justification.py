from settings import ESTIMATE_SPACE, WEIGHTS
import random as r
import forkchoice


class Justification:
    def __init__(self, last_finalized_block=None, latest_messages=dict(), children=dict()):
        self.last_finalized_block = last_finalized_block
        self.latest_messages = latest_messages
        self.children = children

    def is_null(self):
        return self.latest_messages == dict()

    def estimate(self, default=None):
        return forkchoice.get_fork_choice(self.last_finalized_block, self.latest_messages, self.children)
