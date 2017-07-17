import networkx as nx
import matplotlib.pyplot as plt
import pylab
import utils

from math import pi
from bet import Bet
from settings import NUM_VALIDATORS, VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS


class View:
    @profile
    def __init__(self, bets):
        # be safe, type check!
        for b in bets:
            assert isinstance(b, Bet), "...expected only bets in view"

        # now for some assignment...
        self.bets = set()
        self.latest_bets = dict()
        self.vicarious_latest_bets = dict()
        for v in VALIDATOR_NAMES:
            self.vicarious_latest_bets[v] = dict()

        self.add_bets(bets)

    @profile
    def __str__(self):
        s = "View: \n"
        for b in self.bets:
            s += str(b) + "\n"
        return s

    # The estimator function returns the set of max weight estimates
    # This may not be a single-element set because the validator may have an empty view
    @profile
    def estimator(self):
        return utils.get_estimate_from_justification(self.latest_bets)

    # This method returns the set of bets out of showed_bets and their dependency that isn't part of the view
    @profile
    def get_new_bets(self, showed_bets):

        new_bets = set()
        # The memo will keep track of bets we've already looked at, so we don't redo work.
        memo = set()

        # At the start, our working set will be the "showed bets" parameter
        current_set = set(showed_bets)
        while(current_set != set()):

            next_set = set()
            # If there's no bet in the current working set
            for bet in current_set:

                # Which we haven't seen it in the view or during this loop
                if bet not in self.bets and bet not in memo:

                    # But if we do have a new bet, then we add it to our pile..
                    new_bets.add(bet)

                    # and add the best in its justification to our next working set
                    for b in bet.justification.values():
                        next_set.add(b)
                # Keeping a record of very bet we inspect, being sure not to do any extra (exponential complexity) work
                memo.add(bet)

            current_set = next_set

        # After the loop is done, we return a set of new bets
        return new_bets

    # This method updates a validator's observed latest bets (and vicarious latest bets) in response to seeing new bets
    @profile
    def add_bets(self, showed_bets):

        '''
        PART -1 - type check
        '''

        for b in showed_bets:
            assert isinstance(b, Bet), "expected only to add bets"

        '''
        PART 0 - finding newly discovered bets
        '''

        newly_discovered_bets = self.get_new_bets(showed_bets)

        '''
        PART 1 - updating the set of viewed bets
        '''

        for b in newly_discovered_bets:
            self.bets.add(b)

        '''
        PART 2 - updating latest bets
        '''

        # updating latest bets..
        for b in newly_discovered_bets:
            if b.sender not in self.latest_bets:
                self.latest_bets[b.sender] = b
                continue
            if self.latest_bets[b.sender].sequence_number < b.sequence_number:
                self.latest_bets[b.sender] = b
                continue
            assert (b == self.latest_bets[b.sender] or
                    b.is_dependency_from_same_validator(self.latest_bets[b.sender])), "...did not expect any equivocating nodes!"

        '''
        PART 3 - updating vicarious latest bets
        '''

        # updating vicarious_latest_bets for validator v, for all v..
        for v in self.latest_bets:
            self.vicarious_latest_bets[v] = self.latest_bets[v].justification

    @profile
    def get_extension_from_same_validator(self):
        return (self.dependency_from_same_validator()).union(self.bets)

    @profile
    def dependency_from_same_validator(self):
        dependencies = set()
        for bet in self.bets:
            dependencies = dependencies.union(bet.dependency_from_same_validator())

        return dependencies

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
                G.add_edges_from([(e[0], e[1])])

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

        ax = plt.gca()  # to get the current axis
        ax.collections[0].set_edgecolor("black")

        ax.text(-0.05, 0.1, "Weights: ", fontsize=20)

        for v in xrange(NUM_VALIDATORS):
            xpos = (float)(v + 1)/(float)(NUM_VALIDATORS + 1) - 0.01
            ax.text(xpos, 0.1, (str)((int)(WEIGHTS[v])), fontsize=20)

        pylab.show()
