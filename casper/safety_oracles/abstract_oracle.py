"""AbstractOracle defining methods oracles must implement"""
from abc import ABC, abstractmethod


class AbstractOracle(ABC):
    '''Abstract parent class for all oracles'''
    @abstractmethod
    def __init__(self, candidate_estimate, view, validator_set):
        pass

    @abstractmethod
    def check_estimate_safety(self):
        pass
