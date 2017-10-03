import settings as s
from block import Block
from adversary import Adversary
import utils

import copy
import networkx as nx


class Safety_Oracle:

    def __init__(self, candidate_estimate, view):
        if candidate_estimate is None:
            raise Exception("cannot decide if safe without an estimate")

        self.candidate_estimate = candidate_estimate
        self.view = view

    # find biggest set of validators that
    # a) each of their latest messages is on the candidate_estimate
    # b) each of them have seen from eachother a latest message on the candidate_estimate
    # c) none of them can see a new message from another not on the candidate_estimate
    # code is quite verbose for first version readability :)
    @profile
    def find_biggest_clique(self):

        # only consider validators whose messages are compatable w/ candidate_estimate
        with_candidate = {v for v in s.VALIDATOR_NAMES if v in self.view.latest_messages and \
                                 not utils.are_conflicting_estimates(self.candidate_estimate, self.view.latest_messages[v])}

        # do not have safety if less than half have candidate_estimate
        if utils.get_weight(with_candidate) < s.TOTAL_WEIGHT / 2:
            return set()

        edges = []
        #for each pair of validators, v, w, add an edge if...
        pairs = [[v, w] for v in with_candidate for w in with_candidate if v < w]
        for [v, w] in pairs:
            # the latest message v has seen from w is on the candidate estimate
            v_msg = self.view.latest_messages[v]
            if w not in v_msg.justification.latest_messages:
                continue

            w_msg_in_v_view = v_msg.justification.latest_messages[w]
            if utils.are_conflicting_estimates(self.candidate_estimate, w_msg_in_v_view):
                continue

            # the latest block w has seen from v is on the candidate estimate
            w_msg = self.view.latest_messages[w]
            if v not in w_msg.justification.latest_messages:
                continue

            v_msg_in_w_view = w_msg.justification.latest_messages[v]
            if utils.are_conflicting_estimates(self.candidate_estimate, v_msg_in_w_view):
                continue

            # there are no blocks from w, that v has not seen, that might change v's estimate
            if utils.exists_free_message(self.candidate_estimate, w, w_msg_in_v_view.sequence_number, self.view):
                continue

            # there are no blocks from v, that w has not seen, that might change w's estimate
            if utils.exists_free_message(self.candidate_estimate, v, v_msg_in_w_view.sequence_number, self.view):
                continue

            edges.append((v, w))

        G = nx.Graph()

        G.add_edges_from(edges)

        cliques = nx.find_cliques(G)

        max_clique = []

        for c in cliques:
            if utils.get_weight(c) > utils.get_weight(max_clique):
                max_clique = c

        return set(max_clique)


    @profile
    def check_estimate_safety(self):

        biggest_clique = self.find_biggest_clique()

        # minumum amount of weight that has to equivocate
        fault_tolerance = 2 * utils.get_weight(biggest_clique) - s.TOTAL_WEIGHT

        if fault_tolerance > 0:
            clique_weights = {s.WEIGHTS[v] for v in biggest_clique}

            # minimum number of validators that need to equivocate
            equivocating = set()
            while round(sum(equivocating), 2) < round(fault_tolerance, 2): # round to stop issues w/ floating point rounding
                equivocating.add(max(clique_weights.difference(equivocating)))

            # return the number of faults we can tolerate, which is one less than the number that need to equivocate.
            return fault_tolerance, len(equivocating) - 1
        else:
            return 0, 0
