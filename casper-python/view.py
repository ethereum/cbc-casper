import networkx as nx
from networkx.readwrite import json_graph
import sys
import json

from bet import Bet
from settings import NUM_VALIDATORS, VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS

# Views are sets of bets...
# ...with corresponding class functions!
class View:
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

    def add_bet(self, bet):
        self.recompute_extension = True
        self.recompute_latest_bets = True

        # be safe, type check!...
        assert isinstance(bet, Bet), "...expected to add a bet to the view"

        # ...and finally, add the bet!
        self.bets.add(bet)

    def remove_bets(self, bets_to_remove_from_view):
        self.recompute_extension = True
        self.bets.difference_update(bets_to_remove_from_view)

    # the dependency of a view inherits its definition from the dependency of a bet...
    # ...it is union of the dependencies of the bets in the view!

    # THIS CAN BE OPTIMIZED BY, INSTEAD OF RUNNING THE DEPENDENCY FUNCTION FROM THE BET
    # CLASS FOR EVERY BET IN THE VIEW,...
    # ...REWRITING IT SO THAT THE DAG IS NOT REDUNDANTLY TRAVERSED
    def dependency(self):
        dependencies = set()
        for bet in self.bets:
            dependencies = dependencies.union(bet.dependency())

        return dependencies

    # the "extension" of a view is the union of the bets in a view and the bets in its dependency!
    def Extension(self):
        if not self.recompute_extension:
            return self.extension
        # store the extension in the cache
        self.extension = (self.dependency()).union(self.bets)
        self.recompute_extension = False
        return self.extension

    #####################################################################################
    # if A is a dependency of B, B is causally dependent on A...
    # ...which means that B is causally (and therefore chronologically) "later" than A...
    # ...thus the definition of dependency lets us define and identify the latest bets in a given view...
    # ...to reason about consensus in a view, we will need to identify the latest bets from each validator...!
    #####################################################################################

    # this algorithm encodes a map from validators to their lates bets, in a particular view...
    # ...it returns a Python dictionary of the most recent bets, indexed by validator...
    # ...and it stores empty set to handle key exceptions!
    def LatestBets(self):
        if not self.recompute_latest_bets:
            return self.latest_bets

        # here's the dictionary that we'll populate and return
        latest_bets = dict()
        for v in VALIDATOR_NAMES:
            latest_bets[v] = None

        # we are going to search every bet in the extension of view to be sure to find all of the latest bets...
        # ...we'll call the bet we're currently inspecting "candidate"
        for candidate_bet in (self.Extension()):

            # we're going to be filtering first by validator
            sender = candidate_bet.sender

            # if we haven't heard anything from this validator...
            # ...we can trivially say that the candidate is the latest bet we've seen, from this validator..
            if latest_bets[sender] is None:
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
    def canonical_estimate(self):

        # first, grab the latest bets...
        latest_bets = self.LatestBets()

        # now compute the scores of each estimate
        scores = dict.fromkeys(ESTIMATE_SPACE, 0)
        for v in VALIDATOR_NAMES:
            if latest_bets[v] is None:
                continue
            else:
                assert isinstance(latest_bets[v], Bet), "...expected only bets or the emptyset in the latest bets"
                scores[latest_bets[v].estimate] += WEIGHTS[v]

        # get the max score
        max_score = 0
        for e in ESTIMATE_SPACE:
            if scores[e] > max_score:
                max_score = scores[e]
                max_score_estimate = e

        # check that we have a max_score greater than zero:
        # note that here we are requiring the tie-breaking property.
        if max_score > 0:
            return max_score_estimate
        else:
            raise Exception("...expected a non-empty view")

    def plot_view(self, decided):
        nodes = self.Extension()
        graph = {"nodes": [], "links": []}

        def display_height(bet, i=0):
            l = []
            for b in bet.justification:
                l.append(display_height(b, i+1))
            if len(l) > 0:
                return max(l) + 1
            else:
                return 0

        def generate_bet_object(bet):
            return {'id': b.id_number,
                    'group': b.sender,
                    'estimate': b.estimate,
                    'decided': decided[b.sender],
                    'xPos': (float)(b.sender+1)/(float)(NUM_VALIDATORS+1),
                    'yPos': (display_height(b)+1)}

        # Generate the JSON we will use to render the build
        for b in nodes:
            new_bet = generate_bet_object(b)
            if new_bet not in graph['nodes']:
                graph['nodes'].append(new_bet)
            for b2 in b.justification:
                new_bet2 = generate_bet_object(b2)
                if new_bet2 not in graph['nodes']:
                    graph['nodes'].append(new_bet2)
                edge_definition = {'source': b2.id_number, 'target': b.id_number, 'value': 5}
                if edge_definition not in graph['links']:
                    graph['links'].append(edge_definition)
        graph['nodes'] = list(graph['nodes'])

        if __debug__:
            print "decided", decided

        # Check if any of our nodes is undecided. We won't return if that is the case
        is_all_decided = True
        for b in nodes:
            if decided[b.sender] is False:
                is_all_decided = False

        # Let's only return when all the nodes are decided
        if not is_all_decided:
            return

        # We already decided on all nodes, so let's return the data and call it a day!
        print(json.dumps(graph))
        sys.exit(0)
