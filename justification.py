from settings import ESTIMATE_SPACE, WEIGHTS
import utils
import random as r
from block import Block


class Justification:
    def __init__(self, latest_messages=dict(), last_finalized_block=Block()):
        self.last_finalized_block = last_finalized_block
        self.latest_messages = latest_messages

    def is_null(self):
        return self.latest_messages == dict()

    '''
    def estimate(self, default=None):
        return last_finalized_block

        fork choice rule needs to go here

        scores = dict()
        for e in ESTIMATE_SPACE:
            scores[e] = 0

        for v in self.latest_messages:
            scores[self.latest_messages[v].estimate] += WEIGHTS[v]

        mwe = utils.get_max_weight_estimates(scores)

        if default is not None:
            assert default in ESTIMATE_SPACE, "expected default to be an estimate"
            if default in mwe:
                return default

        return r.choice(tuple(mwe))
    '''
