"""The Turan Oracle module implements a very-low bound on safety detection
For details see https://gist.github.com/naterush/d867fe35ecb63c42e6c1f053e2ff33a8
"""

import math

import casper.utils as utils
from casper.safety_oracles.clique_oracle import CliqueOracle


class TuranOracle(CliqueOracle):
    ''' finds the easiest-to-find biggest set (using Turan's Theorem) of validators that
    a) each of their latest messages is on the candidate_estimate
    b) each of them have seen from eachother a latest message on the candidate_estimate
    c) none of them can see a new message from another not on the candidate_estimate
    NOTE: if biggest clique can easily be determined to be < 50% by weight, will
          return with empty set and 0 weight.'''
    def find_biggest_clique(self):
        # Do not have safety if less than half have candidate_estimate.
        if self.validator_set.weight(self.with_candidate) < self.validator_set.weight() / 2:
            return set(), 0

        num_edges = len(self._collect_edges())

        # for reasoning behind this,
        # see https://gist.github.com/naterush/d867fe35ecb63c42e6c1f053e2ff33a8
        min_size_max_clique = int(math.ceil(
            float(math.pow(len(self.validator_set), 2)) /
            float(math.pow(len(self.validator_set), 2) - 2 * num_edges)
        ))

        sorted_validators = self.validator_set.sorted_by_weight()
        max_clique = set(sorted_validators[:min_size_max_clique])

        return max_clique, utils.get_weight(max_clique)
