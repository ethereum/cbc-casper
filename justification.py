import random as r
import forkchoice


class Justification:
    def __init__(self, last_finalized_block=None, latest_messages=dict()):
        self.last_finalized_block = last_finalized_block
        self.latest_messages = dict()
        for v in latest_messages:
            self.latest_messages[v] = latest_messages[v]

    def is_null(self):
        return self.latest_messages == dict()
