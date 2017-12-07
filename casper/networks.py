import random as r

from casper.network import Network


class SynchronousNetwork(Network):
    def delay(self, sender, receiver):
        return 0


class StepNetwork(Network):
    def delay(self, sender, receiver):
        return 1


class ConstantDelayNetwork(Network):
    CONSTANT = 5

    def delay(self, sender, receiver):
        return self.CONSTANT


class LinearDelayNetwork(Network):
    MAX_DELAY = 5

    def delay(self, sender, receiver):
        return r.randint(1, self.MAX_DELAY)


class GaussianDelayNetwork(Network):
    MU = 10
    SIGMA = 5
    MIN_DELAY = 1

    def delay(self, sender, receiver):
        random_delay = round(r.gauss(self.MU, self.SIGMA))
        return max(self.MIN_DELAY, random_delay)
