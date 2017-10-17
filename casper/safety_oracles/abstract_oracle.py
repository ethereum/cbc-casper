from abc import ABC, abstractmethod

class AbstractOracle(ABC):
    @abstractmethod
    def __init__(self, candidate_estimate, view, validator_set):
        pass

    @abstractmethod
    def check_estimate_safety(self):
        pass
