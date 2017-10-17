"""The clique oracle module ... """
import itertools
import networkx as nx
from casper.safety_oracles.abstract_oracle import AbstractOracle

import casper.utils as utils


class CliqueOracle(AbstractOracle):
    """A clique safety oracle detecting safety from validators committed to an estimate."""

    def __init__(self, candidate_estimate, view, validator_set):
        if candidate_estimate is None:
            raise Exception("cannot decide if safe without an estimate")

        self.candidate_estimate = candidate_estimate
        self.view = view
        self.validator_set = validator_set
        # Only consider validators whose messages are compatable w/ candidate_estimate.
        self.with_candidate = {
            v for v in self.validator_set if v in self.view.latest_messages and
            not utils.are_conflicting_estimates(
                self.candidate_estimate,
                self.view.latest_messages[v]
            )
        }

    def _collect_edges(self):
        edges = []
        # For each pair of validators, val1, val2, add an edge if:
        for val1, val2 in itertools.combinations(self.with_candidate, 2):
            # the latest message val1 has seen from val2 is on the candidate estimate,
            v1_msg = self.view.latest_messages[val1]
            if val2 not in v1_msg.justification.latest_messages:
                continue

            v2_msg_in_v1_view = v1_msg.justification.latest_messages[val2]
            if utils.are_conflicting_estimates(self.candidate_estimate, v2_msg_in_v1_view):
                continue

            # the latest block val2 has seen from val1 is on the candidate estimate
            v2_msg = self.view.latest_messages[val2]
            if val1 not in v2_msg.justification.latest_messages:
                continue

            v1_msg_in_v2_view = v2_msg.justification.latest_messages[val1]
            if utils.are_conflicting_estimates(self.candidate_estimate, v1_msg_in_v2_view):
                continue

            # there are no blocks from val2, that val1 has not seen;
            # that might change validators' estimate.
            if utils.exists_free_message(self.candidate_estimate, val2,
                                         v2_msg_in_v1_view.sequence_number, self.view):
                continue

            # and if there are no blocks from val1, that val2 has not seen,
            # that might change val2's estimate.
            if utils.exists_free_message(self.candidate_estimate, val1,
                                         v1_msg_in_v2_view.sequence_number, self.view):
                continue

            edges.append((val1, val2))

        return edges

    # Find biggest set of validators that
    # a) each of their latest messages is on the candidate_estimate
    # b) each of them have seen from eachother a latest message on the candidate_estimate
    # c) none of them can see a new message from another not on the candidate_estimate
    # NOTE: if biggest clique can easily be determined to be < 50% by weight, will
    #       return with empty set and 0 weight.
    def find_biggest_clique(self):
        """Finds the biggest clique of validators committed to target estimate."""

        # Do not have safety if less than half have candidate_estimate.
        if self.validator_set.weight(self.with_candidate) < self.validator_set.weight() / 2:
            return set(), 0

        edges = self._collect_edges()
        G = nx.Graph()
        G.add_edges_from(edges)
        cliques = nx.find_cliques(G)

        max_clique = []
        max_weight = 0
        for clique in cliques:
            test_weight = utils.get_weight(clique)
            if test_weight > max_weight:
                max_clique = clique
                max_weight = test_weight

        return set(max_clique), max_weight

    def check_estimate_safety(self):
        """Returns lower bound on amount of fault tolerance some estimate has."""

        biggest_clique, clique_weight = self.find_biggest_clique()

        # Minumum amount of weight that has to equivocate.
        fault_tolerance = 2 * clique_weight - self.validator_set.weight()

        if fault_tolerance > 0:
            clique_weights = {v.weight for v in biggest_clique}

            # Minimum number of validators that need to equivocate.
            equivocating = set()

            # Round to stop issues w/ floating point rounding.
            while round(sum(equivocating), 2) < round(fault_tolerance, 2):
                equivocating.add(max(clique_weights.difference(equivocating)))

            # Return the number of faults we can tolerate, which is one less
            # than the number that need to equivocate.
            return fault_tolerance, len(equivocating) - 1
        else:
            return 0, 0
