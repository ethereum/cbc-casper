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
    # a) each of their latest blocks in on the candidate_estimate
    # b) each of them have seen from eachother a latest block on the candidate_estimate
    # c) none of them can see a new block from another not on the candidate_estimate
    # code is quite verbose for first version readability :)
    @profile
    def find_biggest_clique(self):

        # only consider validators building on candidate_estimate
        building_on_candidate = {v for v in s.VALIDATOR_NAMES if v in self.view.latest_messages and \
                                self.candidate_estimate.is_in_blockchain(self.view.latest_messages[v])}

        # do not have safety if less than half are building on the candidate_estimate
        if utils.get_weight(building_on_candidate) < s.TOTAL_WEIGHT / 2:
            return set()

        edges = []
        #for each pair of validators, v, w, add an edge if...
        pairs = [[v, w] for v in building_on_candidate for w in building_on_candidate if v < w]
        for [v, w] in pairs:
            # the latest block v has seen from w is on the candidate estimate
            v_msg = self.view.latest_messages[v]
            if w not in v_msg.justification.latest_messages:
                continue

            w_msg_in_v_view = v_msg.justification.latest_messages[w]
            if not self.candidate_estimate.is_in_blockchain(w_msg_in_v_view):
                continue

            # the latest block w has seen from v is on the candidate estimate
            w_msg = self.view.latest_messages[w]
            if v not in w_msg.justification.latest_messages:
                continue

            v_msg_in_w_view = w_msg.justification.latest_messages[v]
            if not self.candidate_estimate.is_in_blockchain(v_msg_in_w_view):
                continue

            dont_add = False
            # there are no blocks from w, that v has not seen, that might change v's estimate
            w_later_blocks = utils.get_later_messages_from_val(w, w_msg_in_v_view.sequence_number, w_msg)
            for b in w_later_blocks:
                if not self.candidate_estimate.is_in_blockchain(b):
                    dont_add = True

            # there are no blocks from v, that w has not seen, that might change w's estimate
            v_later_blocks = utils.get_later_messages_from_val(v, v_msg_in_w_view.sequence_number, v_msg)
            for b in v_later_blocks:
                if not self.candidate_estimate.is_in_blockchain(b):
                    dont_add = True

            if not dont_add:
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

        for v in s.VALIDATOR_NAMES:
            if v not in self.view.latest_messages:
                return 0, 0

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
