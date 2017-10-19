import sys


class SimulationRunner:
    def __init__(self, validator_set, msg_gen, total_rounds=None):
        self.validator_set = validator_set
        self.msg_gen = msg_gen

        if total_rounds is None:
            self.total_rounds = sys.maxsize
        else:
            self.total_rounds = total_rounds

        self.round = 0

    def run(self):
        """ run simulation total_rounds if specified
            otherwise, run indefinitely """
        pass

    def step(self):
        """ run one round of the simulation """
        self.round += 1
        pass
