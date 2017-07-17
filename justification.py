from settings import ESTIMATE_SPACE, WEIGHTS
import utils
import random as r


class Justification:
    def __init__(self, latest_bets=dict()):
        self.latest_bets = dict()
        if latest_bets == dict():
            return

        for v in latest_bets:
            self.latest_bets[v] = latest_bets[v]

    def is_null(self):
        return self.latest_bets == dict()

    def estimate(self, default=None):
        scores = dict()
        for e in ESTIMATE_SPACE:
            scores[e] = 0

        for v in self.latest_bets:
            scores[self.latest_bets[v].estimate] += WEIGHTS[v]

        mwe = utils.get_max_weight_estimates(scores)

        if default is not None:
            assert default in ESTIMATE_SPACE, "expected default to be an estimate"
            if default in mwe:
                return default

        return r.choice(tuple(mwe))
