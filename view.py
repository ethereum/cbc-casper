import networkx as nx
import matplotlib.pyplot as plt
import pylab
import utils

from math import pi
from bet import Bet
from settings import NUM_VALIDATORS, VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS

# Views are sets of bets...
# ...with corresponding class functions!


class View:
    @profile
    def __init__(self, bets):
        # be safe, type check!
        for b in bets:
            assert isinstance(b, Bet), "...expected only bets in view"

        # now for some assignment...
        self.bets = set()
        for b in bets:
            self.bets.add(b)

        # to avoid recomputing the view's extension, when this is false we return a cached value
        self.recompute_extension = True
        self.recompute_latest_bets = True

    # this "serialization" has a new line for every serialization of bets...
    # ...so that it literally looks just like this...!
    # View:
    # (1, {(1, {}, 0)}, 1)
    # (0, {}, 0)

    def __str__(self):
        s = "View: \n"
        for b in self.bets:
            s += str(b) + "\n"
        return s

    @profile
    def add_bet(self, bet):
        self.recompute_extension = True
        self.recompute_latest_bets = True

        # be safe, type check!...
        assert isinstance(bet, Bet), "...expected to add a bet to the view"

        # ...and finally, add the bet!
        self.bets.add(bet)

    @profile
    def add_view(self, view):
        for b in view.bets:
            self.add_bet(b)

    @profile
    def remove_bets(self, bets_to_remove_from_view):
        self.recompute_extension = True
        self.bets.difference_update(bets_to_remove_from_view)

    # the dependency of a view inherits its definition from the dependency of a bet...
    # ...it is union of the dependencies of the bets in the view!

    # THIS CAN BE OPTIMIZED BY, INSTEAD OF RUNNING THE DEPENDENCY FUNCTION FROM THE BET
    # CLASS FOR EVERY BET IN THE VIEW,...
    # ...REWRITING IT SO THAT THE DAG IS NOT REDUNDANTLY TRAVERSED

    @profile
    def dependency(self):
        dependencies = set()
        for bet in self.bets:
            dependencies = dependencies.union(bet.dependency())

        return dependencies

    # the "extension" of a view is the union of the bets in a view and the bets in its dependency!
    @profile
    def get_extension(self):
        return (self.dependency()).union(self.bets)

    @profile
    def dependency_from_same_validator(self):
        dependencies = set()
        for bet in self.bets:
            dependencies = dependencies.union(bet.dependency_from_same_validator())

        return dependencies

    @profile
    def get_extension_from_same_validator(self):
        return (self.dependency_from_same_validator()).union(self.bets)

    @profile
    def get_extension_up_to_sequence_numbers(self, sequence_numbers):

        sieve = set(self.bets)
        extension = set()

        while(sieve != set()):

            to_remove_from_sieve = []
            to_add_to_sieve = []

            for bet in sieve:

                to_remove_from_sieve.append(bet)

                if bet.sender not in sequence_numbers or bet.sequence_number > sequence_numbers[bet.sender]:
                    extension.add(bet)

                    for b in bet.justification.values():
                        to_add_to_sieve.append(b)

            for b in to_remove_from_sieve:
                sieve.remove(b)

            for b in to_add_to_sieve:
                sieve.add(b)

        return extension

    #####################################################################################
    # if A is a dependency of B, B is causally dependent on A...
    # ...which means that B is causally (and therefore chronologically) "later" than A...
    # ...thus the definition of dependency lets us define and identify the latest bets in a given view...
    # ...to reason about consensus in a view, we will need to identify the latest bets from each validator...!
    #####################################################################################

    # this algorithm encodes a map from validators to their lates bets, in a particular view...
    # ...it returns a Python dictionary of the most recent bets, indexed by validator...
    # ...and it stores empty set to handle key exceptions!
    @profile
    def get_latest_bets(self):
        if not self.recompute_latest_bets:
            return self.latest_bets

        # here's the dictionary that we'll populate and return
        latest_bets = dict()

        # we are going to search every bet in the extension of view to be sure to find all of the latest bets...
        # ...we'll call the bet we're currently inspecting "candidate"
        for candidate_bet in (self.get_extension()):

            # we're going to be filtering first by validator
            sender = candidate_bet.sender

            # if we haven't heard anything from this validator...
            # ...we can trivially say that the candidate is the latest bet we've seen, from this validator..
            if sender not in latest_bets:
                latest_bets[sender] = candidate_bet
                continue  # ...and then we're totally free to go to the next candidate!

            # if we already have a latest bet from this validator...
            # ...we need to check if the candidate is "later" or "earlier" than this bet...
            # ...and then update our record of the latest bet from this validator, if appropriate

            # so if the candidate is in the dependency the latest bet...
            # ...then the candidate earlier than that "latest bet"...
            # ...so the candidate definitely is not the latest bet in the view...!
            if candidate_bet.is_dependency(latest_bets[sender]):
                continue  # to the next candidate!

            # ...if the latest bet is a dependency of the candidate bet...
            # ...then this candidate is "later" than our current "latest bet"
            if latest_bets[sender].is_dependency(candidate_bet):
                latest_bets[sender] = candidate_bet  # ...so we keep a record of the latest bets
                continue

            raise Exception("...did not expect any Byzantine (equivocating) validators!")

        # after we filter through all of the bets in the extended view...
        # ...we have our epic dictionary of latest bets!
        self.recompute_extension = True
        self.latest_bets = True
        return latest_bets

    # this computes the maximum weight estimate from the latest bets in the view
    @profile
    def canonical_estimate(self):

        # first, grab the latest bets...
        latest_bets = self.get_latest_bets()

        # now compute the scores of each estimate
        scores = dict.fromkeys(ESTIMATE_SPACE, 0)
        for v in VALIDATOR_NAMES:
            if v not in latest_bets[v]:
                continue
            else:
                assert isinstance(latest_bets[v], Bet), "...expected only bets or the emptyset in the latest bets"
                scores[latest_bets[v].estimate] += WEIGHTS[v]

        max_weight_estimates = get_max_weight_estimates(scores)

        if len(max_weight_estimates) == 1:
            return next(iter(max_weight_estimates))
        else:
            raise Exception("...expected a non-empty view")

    @profile
    def plot_view(self, coloured_bets, colour='green', use_edges=[]):

        G = nx.DiGraph()

        nodes = self.get_extension_from_same_validator()



        for b in nodes:
            G.add_edges_from([(b, b)])

        if use_edges == []:
            for b in nodes:
                for b2 in b.justification.values():
                    G.add_edges_from([(b2, b)])
        else:
            for e in use_edges:
                G.add_edges_from([(e[0],e[1])])

        # G.add_edges_from([('A', 'B'),('C','D'),('G','D')])
        # G.add_edges_from([('C','F')])

        positions = dict()

        for b in nodes:
            positions[b] = (float)(b.sender + 1)/(float)(NUM_VALIDATORS + 1), 0.2 + 0.1*b.height

        node_color_map = {}
        for b in nodes:
            if b in coloured_bets:
                node_color_map[b] = colour
            else:
                node_color_map[b] = 'white'

        color_values = [node_color_map.get(node) for node in G.nodes()]

        labels = {}
        for b in nodes:
            labels[b] = b.estimate
        # labels['B']=r'$b$'

        node_sizes = [700*pow(WEIGHTS[node.sender]/pi, 0.5) for node in G.nodes()]

        nx.draw_networkx_labels(G, positions, labels, font_size=20)

        nx.draw(G, positions, node_color=color_values, node_size=node_sizes, edge_color='black', edge_cmap=plt.cm.Reds)

        ax = plt.gca() # to get the current axis
        ax.collections[0].set_edgecolor("black")


        ax.text(-0.05,0.1,"Weights: ",fontsize=20)

        for v in xrange(NUM_VALIDATORS):
            xpos = (float)(v + 1)/(float)(NUM_VALIDATORS + 1) - 0.01
            ax.text(xpos,0.1,(str)((int)(WEIGHTS[v])),fontsize=20)

        pylab.show()