'''
Casper PoC: Correct-by-construction asynchronous binary consensus.

Note that comments marked with "#########....#########"" barriers are probably
conceptually important Other comments may be conceptually important but are
mostly for code comprehension Note that not all comments have been marked up in
this manner, yet... :)
'''
import copy   # hopefully this does not end up being used
import random as r  # to ensure the tie-breaking property
# this stuff is for plotting the dag:
import networkx as nx
import matplotlib.pyplot as plt
import pylab

from settings import NUM_VALIDATORS, VALIDATOR_NAMES, BIGINT

r.seed()


'''
Global variables
'''

# here they are... !
WEIGHTS = dict()
for v in VALIDATOR_NAMES:
    WEIGHTS[v] = 100.0 + v + 1/(float)(BIGINT + r.randint(1, BIGINT))

# behold, the binary estimate space!...
# it's a bit underwhelming, sure, but it's foundational
ESTIMATE_SPACE = set([0, 1])


# this is only to be used for debugging, pls forget about it
bet_number = 0


'''
Casper stuff
'''


# the Bet class implements a DAG of bets...
# ...every bet has a sender, an estimate, and a justification (which is itself
# a set of bets or the empty set)
class Bet:
    # we're now going to define the bet constructor (__init__), equality realtion (__eq__), string serialization (__str__), and hash (__hash__)...
    # ...these things are not very conceptually important...

    # constructor!
    def __init__(self, estimate, justification, sender):

        # be safe. type check!...
        assert sender in VALIDATOR_NAMES, "...expected a validator!"
        assert estimate in ESTIMATE_SPACE, "...expected an estimate!"
        for b in justification:  # anything iterable, containing bets
            assert isinstance(b, Bet), "...expected there to be only bets in the justification!"

        # ...then do some assignment
        self.sender = sender
        self.estimate = estimate
        self.justification = set()
        for b in justification:
            self.justification.add(b)

        # ...sorting some things out just for debugging please ignore this!
        global bet_number
        self.id_number = "validator " + str(sender) + ", bet_num " + str(bet_number)
        bet_number += 1

    # equality check
    def __eq__(self, B):

        # the empty set is not a bet!
        # this saves us from doing if isinstance(b,Bet) and b == set() every time we need to check if we're holding a set() instead of a Bet
        if B is None:
            return False

        # ...but first be safe. type check!
        assert isinstance(B, Bet), "Expected bet as parameter in `=='"

        # two bets are equal only if they have the same estimate, sender and justification...
        # ...it turns out that __eq__ in python's set() uses __eq__ of its members if available, under the hood...
        # ...so this turns out to be a recursive definition! yay, recursion!
        if self.estimate != B.estimate \
            or self.sender != B.sender \
            or B.justification != self.justification:
            return False
        return True

    # this serializes bets nicely, like this: "(1, {(1, {}, 0)}, 1)"...!
    def __str__(self):
        string = "("
        string += str(self.estimate) + ", {"
        i = 0
        # if this following line of code sometimes produces different orders (justification is a set), then we have an issue.
        # it would be good practice to give a standard for ordering bets in justifications.
        for b in self.justification:
            string += str(b)
            i += 1
            if i != len(self.justification):  # getting fancy; leaving out commas without successive terms
                string += ", "
        string += "}, " + str(self.sender) + ")"
        return string

    # it turns out that to make a set of something in Python, it needs to be hashable!...
    # ...btw it would be cool to show that for two bets A, B with A == B implies str(A) == str(B),..
    # ...which more trivially implies hash(A) == hash(B)...
    # ...so that we don't need to think about counterintuive Python set() behaviour...
    # ...for example if we have set([A]).add(B) = set([A,B]) with hash(A) != hash(B) even though A == B!
    def __hash__(self):
        return hash(str(self))

    #####################################################################################
    # a bet A is a dependency of a bet B if either...
    # ...A is in the justification of B...
    # ...or A is in the dependency of bets in the justification of B!
    #####################################################################################

    # this function checks if this bet (self) is a dependency of some bet B...
    def is_dependency(self, B):

        # be safe, type check!
        assert isinstance(B, Bet), "...expected a bet!"

        # self is definitely a dependency of B if it is in the justification...
        if self in B.justification:
            return True

        # ...or if it is in the dependency of anything in the justification!
        for b in B.justification:
            if self.is_dependency(b):
                return True

        # if neither of these, then "self" is not a dependency of B!
        return False

    # this one gets all the bets in the dependency of this bet (self)...
    # ...it puts them into a set, and returns that!

    # THIS NEEDS TO BE OPTIMIZED WITH MEMOIZATION TO NOT RE-TRAVERSE DAT DAG
    def dependency(self):
        dependencies = set()

        # recurr into the justification to find all dependencies and add them to our set "d"
        def recurr(B):
            for b in B.justification:  # recursion bottoms on empty iterable
                dependencies.add(b)  # note that .add in set() checks if __hash__ does not already appear!
                recurr(b)

        # now we're calling it:
        recurr(self)

        # we did it!
        return dependencies


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

        # be safe, type check!...
        assert isinstance(bet, Bet), "...expected to add a bet to the view"

        # ...and finally, add the bet!
        self.bets.add(bet)

    # the dependency of a view inherits its definition from the dependency of a bet...
    # ...it is union of the dependencies of the bets in the view!

    # THIS CAN BE OPTIMIZED BY, INSTEAD OF RUNNING THE DEPENDENCY FUNCTION FROM THE BET CLASS FOR EVERY BET IN THE VIEW,...
    # ...REWRITING IT SO THAT THE DAG IS NOT REDUNDANTLY TRAVERSED
    def dependency(self):

        dependencies = set()
        for bet in self.bets:
            dependencies = dependencies.union(bet.dependency())

        return dependencies

    # the "extension" of a view is the union of the bets in a view and the bets in its dependency!
    def Extension(self):
        return (self.dependency()).union(self.bets)


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

        G = nx.DiGraph()

        nodes = self.Extension()

        for b in nodes:
            G.add_edges_from([(b, b)])
            for b2 in b.justification:
                G.add_edges_from([(b2, b)])


        # G.add_edges_from([('A', 'B'),('C','D'),('G','D')])
        # G.add_edges_from([('C','F')])

        print "decided", decided

        def display_height(bet, i=0):

            l = []
            for b in bet.justification:
                l.append(display_height(b, i+1))

            if len(l) > 0:
                return max(l) + 1
            else:
                return 0



        positions = dict()

        for b in nodes:
            positions[b] = (float)(b.sender+1)/(float)(NUM_VALIDATORS+1), (display_height(b)+1)/4.


        node_color_map = {}
        for b in nodes:
            if decided[b.sender] is True:
                node_color_map[b] = 'green'
            else:
                node_color_map[b] = 'white'

        color_values = [node_color_map.get(node) for node in G.nodes()]

        labels = {}
        for b in nodes:
            labels[b] = b.estimate
        # labels['B']=r'$b$'

        nx.draw_networkx_labels(G, positions, labels, font_size=20)

        nx.draw(G, positions, node_color=color_values, node_size=1500, edge_color='black', edge_cmap=plt.cm.Reds)
        pylab.show()





# The ideal adversary uses the following class to model validators
# The validators will be running a "less safe" version of casper...
# ...one where observing a new latest bet from vi does not (ever, as a rule) change the latest bets you've observed from vj != vi

# this class has the folowing attributes:
# model_of
# my_latest_bet
# viewable   #MAYBE QUESTIONABLE DESIGN CHOICE - PERHAPS THE SET OF VIEWABLE BETS FOR A VALIDATOR SHOULD NOT BE A PART OF THE VALIDATOR MODEL
# latest_oberved_bets

class Model_Validator:
    def __init__(self, model_of_validator, view):

        # lets keep a record of the validator that the model is of...
        # this is useful for adding bets from this validator using class functions other than __init__
        assert model_of_validator in VALIDATOR_NAMES, "expected validator in __init__ of Model_Validator"
        self.model_of = model_of_validator

        # for good measure, lets make sure that we really have a view, here...
        assert isinstance(view, View), "expected view in __init__ of Model_Validator"

        self.my_latest_bet = view.LatestBets()[self.model_of]

        # These are the bets the validator "can see" from a view given by self.my_latest_bet...
        # ...in the sense that these bets are not already in the extension of its view
        self.viewable = dict()
        for v in VALIDATOR_NAMES:
            self.viewable[v] = set()

        # will track the latest bets observed by this model validator
        self.latest_observed_bets = dict()

        # if this validator has no latest bets in the view, then we store...
        if self.my_latest_bet is None:

            # ...an empty dictionary of latest observed bets...
            for v in VALIDATOR_NAMES:
                self.latest_observed_bets[v] = None

            # for validators without anything in their view, any bets are later bets are viewable bets!
            # ...so we add them all in!
            for b in view.Extension():
                self.viewable[b.sender].add(b)

        # if we do have a latest bet from this validator, then...
        else:
            assert isinstance(self.my_latest_bet, Bet), "...expected my_latest_bet to be a bet or the empty set"

            # we can get the latest bets in our standard way
            my_view = View(set([self.my_latest_bet]))
            self.latest_observed_bets = my_view.LatestBets()

            # then all bets that are causally after these bets are viewable by this validator
            for b in view.Extension():
                # ...we use the is_dependency relation to test if b is causally after the latest bet observed from that sender
                if self.latest_observed_bets[b.sender] is None:
                    self.viewable[b.sender].add(b)
                else:
                    assert isinstance(self.latest_observed_bets[b.sender], Bet), "...expected dictionary latest_observed_bets to only contain values of a bet or the empty set"

                    # if b is later than the latest observed bet from b.sender, then b is viewable to this model validator
                    if self.latest_observed_bets[b.sender].is_dependency(b):
                        self.viewable[b.sender].add(b)



    # model validators use their view at my_latest_bet to calculate an estimate, returns set() on failure
    def my_estimate(self):

        # otherwise we compute the max score byzantine free estimate
        scores = dict.fromkeys(ESTIMATE_SPACE, 0)

        for v in VALIDATOR_NAMES:
            if self.latest_observed_bets[v] is None:
                continue
            else:
                assert isinstance(self.latest_observed_bets[v], Bet), "...expected dictionary latest_observed_bets to only contain values of a bet or the empty set"
                scores[self.latest_observed_bets[v].estimate] += WEIGHTS[v]

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


    # this important method makes a bet viewable to the model validator
    # It will only succeed if:
    # * the latest bet from the sender in its dependency
    # * or we haven't heard from the sender before
    def make_viewable(self, bet):

        # be safe, type check.
        assert isinstance(bet, Bet), "...expected a bet!"

        # If we haven't observed anything yet, anything is viewable!
        if self.latest_observed_bets[bet.sender] is None:
            self.viewable[bet.sender].add(bet)
            return True
        else:
            assert isinstance(self.latest_observed_bets[bet.sender], Bet), "...expected dictionary latest_observed_bets to only contain values of a bet or the empty set"
            # This is the "normal case", where a bet from a validator is viewable only if the latest bet is in its dependency
            if self.latest_observed_bets[bet.sender].is_dependency(bet):
                self.viewable[bet.sender].add(bet)
                return True
            else:
                return False

    # this method goes through the viewables and removes any bets that are a dependency latest bets from the same sender
    # this function should be run every time a model validator is shown a new latest_bet
    def update_viewable(self):

        # ...looping over the validators
        for v in VALIDATOR_NAMES:

            # ...if we do have a latest bet from them...
            if self.latest_observed_bets[v] is None:
                continue
            else:
                assert isinstance(self.latest_observed_bets[v], Bet), "...expected dictionary latest_observed_bets to only contain values of a bet or the empty set"

                # then we can remove all bets in viewable which are dependencies of this latest bet...
                # ...but we can't remove them during the iteration, so we store the bets to be removed in this set...
                to_remove_from_viewable = set()

                for b in self.viewable[v]:
                    if b.is_dependency(self.latest_observed_bets[v]):
                        to_remove_from_viewable.add(b)

                # finally, updating the viewable for this validator
                self.viewable[v] = self.viewable[v].difference(to_remove_from_viewable)


    # This function attempts to make a new latest bet for this validator (self) with a given estimate
    def make_new_latest_bet_with_estimate(self, target_estimate):

        # be safe, type check!
        assert target_estimate in ESTIMATE_SPACE, "...expected an estimate!"

        if self.my_latest_bet is None:
            new_bet = Bet(target_estimate, [], self.model_of)
            self.my_latest_bet = new_bet
            return new_bet

        # ...staying safe!
        assert isinstance(self.my_latest_bet, Bet), "...expected my_latest_bet to be a Bet (or the empty set)"  # empty set would have led to a return above

        # if this validator already has the target estimate as its single latest bet, do nothing... 0,0,1,1
        if self.my_latest_bet.estimate == target_estimate:
            return self.my_latest_bet

        # for each validator..
        for v in VALIDATOR_NAMES:

            if self.latest_observed_bets[v] is None or self.latest_observed_bets[v].estimate != target_estimate:

                # and if their latest estimate is not the target estimate...

                # ... in the set of their bets "viewable" to this validator...
                # (note our reliance on the viewable set to make latest bets)
                for b in self.viewable[v]:
                    # ...and if we find one with the target estimate
                    if b.estimate == target_estimate:
                        self.latest_observed_bets[v] = b
                        break


        # recall that we need to update the viewable set after making any changes to the latest bets!
        self.update_viewable()

        # if the validators' potential new canonical estimator is target estimate...
        # ...then we'll make a new bet with that estimate and return it...
        # ...otherwise we throw an exception

        try:

            if self.my_estimate() == target_estimate:

                justification = set()
                for v in VALIDATOR_NAMES:
                    if self.latest_observed_bets[v] is not None:
                        justification.add(self.latest_observed_bets[v])

                # make the new bet
                new_latest_bet = Bet(target_estimate, justification, self.model_of)

                # and update the model parameters accordingly:
                self.my_latest_bet = new_latest_bet

                # finally return
                return new_latest_bet
            else:
                raise Exception("Unable to make legal bet with the target estimate at the given position")
        except:
            raise Exception("...expected a non-empty view")






# the Adversary class has the properties:
# victim_estimate
# target_estimate
# attack_view
# validator_models
# attack_surface
# voting_with_attacker
# voting_against_attacker
# not_voted_yet
# latest_bets
# weight_of_victim_estimate
# weight_of_target_estimate
# attack_delta
# operation_log


class Adversary:
    def __init__(self, view, victim_estimate):

        # be safe! start with type checking.
        assert isinstance(view, View), "...expected a View!"
        assert victim_estimate in ESTIMATE_SPACE, "...expected an estimate!"

        # The adversary has particular estimate that she wants to attack (the victim estimate)...
        self.victim_estimate = victim_estimate

        # ...and a particular estimate she wants to cause to win (the target estimate)...
        self.target_estimate = 1 - victim_estimate  # this will need to change when we go from binary to n-ary

        # the attacker keeps a copy of the parameter view, to which she will add attacking bets...
        self.attack_view = copy.deepcopy(view)

        # ...and she also keeps models of every validator!
        self.validator_models = dict()
        for v in VALIDATOR_NAMES:
            self.validator_models[v] = Model_Validator(v, view)

        # she's going to use this dictionary to keep track of the attack surface
        self.attack_surface = dict()
        for v in VALIDATOR_NAMES:
            self.attack_surface[v] = dict.fromkeys(VALIDATOR_NAMES, True)


        # our adversary is going to classify non-Byzantine validators into the following categories...
        self.voting_with_attacker = set()
        self.voting_against_attacker = set()
        self.not_voted_yet = set()


        # ...and she will keep track of the latest estimates from these validators, if unique
        self.latest_bets = view.LatestBets()

        for v in VALIDATOR_NAMES:
            if self.latest_bets[v] is None:
                self.not_voted_yet.add(v)
            else:
                assert isinstance(self.latest_bets[v], Bet), "...expected latest_bets to have None or a Bet"
                if self.latest_bets[v].estimate == self.victim_estimate:  # if v's latest estimate is the victim estimate...
                    self.voting_against_attacker.add(v)  # ... then v is "voting against" the attacker
                elif self.latest_bets[v].estimate == self.target_estimate:  # if v's latest estimate is the target estimate...
                    self.voting_with_attacker.add(v)  # ...great! v is helping the attacker!

        # if you're voting with the attacker...
        # ...she'll take you out of the attack surface!
        for v in self.voting_with_attacker:
            self.attack_surface.pop(v)

        # The attacker will also keep a close eye on the weights of the victim and target estimates:
        self.weight_of_victim_estimate = 0
        for v in self.voting_against_attacker:
            self.weight_of_victim_estimate += WEIGHTS[v]

        self.weight_of_target_estimate = 0
        for v in self.voting_with_attacker:
            self.weight_of_target_estimate += WEIGHTS[v]

        # the "attack delta" is "the advantage" of the victim estimate over the target estimate
        self.attack_delta = self.weight_of_victim_estimate - self.weight_of_target_estimate

        # the attacker produces a log of the bets added during the attack...
        self.operations_log = []


    # this method updates the attack delta using the Adversary's record of the victim and target estimate weights...
    def update_attack_delta(self):
        self.attack_delta = self.weight_of_victim_estimate - self.weight_of_target_estimate

    # ...and this one returns "True" if the attack delta is less than or equal to zero (indicating target weight >= victim weight)...
    # ...and it returns "False" otherwise...
    def is_attack_complete(self):
        if self.attack_delta <= 0:
            return True
        else:
            return False



    # this method implements an ideal network attack...
    # ...it returns the pair (True, self.operation_log) if the attack is successful
    # ...and (False, self.operatrion_log) otherwise
    def ideal_network_attack(self):

        # We'll continue the attack until we no longer make progress
        # Or until the attack is successful and the victim estimate dethroned
        progress_made = True
        while progress_made:
            progress_made = False


            # the "network-only" attack has two phases...
            #  1) adding bets (with the target estimate) from unobserved validators
            #  2) adding new latest bets (with the target estimate) from validators currently voting against the attacker


            ######
            # Phase 1: observing unobserved validators
            ######

            # the for loop here well de-facto only be executed once...
            # ...because not_voted_yet == set() after ths first complete iteration!
            for v in self.not_voted_yet:

                # these ones are easy...!
                new_bet = self.validator_models[v].make_new_latest_bet_with_estimate(self.target_estimate) # btw: never returns an exception

                # ...becuase progress here is guaranteed!
                progress_made = True

                # so lets make a log of our operations...
                self.operations_log.append(["bet added from previously-unobserve validator", str(new_bet)])

                # ...update validator status...
                # ...remove v from "has_not_voted" and add to "voting_with_attacker"...
                self.voting_with_attacker.add(v)

                # ...remove v from the attack surface...
                self.attack_surface.pop(v)

                # ...update weights + attack delta...
                self.weight_of_target_estimate += WEIGHTS[v]

                # ...add new bet to the latest_bets vector...
                self.latest_bets[v] = new_bet

                # ...make this bet viewable to all those still voting against the attacker
                for v2 in self.voting_against_attacker:
                    self.validator_models[v2].make_viewable(new_bet)

                # ...update the attack view...
                self.attack_view.add_bet(new_bet)

                # ...and update the attack delta!
                self.update_attack_delta()

                # if we can end the attack, then lets return our success
                if self.is_attack_complete():
                    return True, self.operations_log

            # updating the set of validators who haven't voted yet...
            # ...to the empty set, because after this loop all validators have voted.
            self.not_voted_yet = set()


            ######
            # Phase 2: "voting against" validators
            ######


            # we cannot change the size of the interable while iterating over it...
            # ...so we're going to collect the validators we want to remove from "voting against", here...
            # ...and remove them all at once, when we reach the end of the for loop!
            to_remove_from_voting_against_attacker = set()

            # For each validator who is voting against the attacker..
            for v in self.voting_against_attacker:

                # lets have a quick precautionary sanity check...!
                assert isinstance(self.latest_bets[v], Bet), "...expected validators voting_against_attacker to have exactly one latest bet"

                # ...try to add a new bet from this validator with the estimate of the attacker's choosing
                try:
                    new_bet = self.validator_models[v].make_new_latest_bet_with_estimate(self.target_estimate)

                # If we failed to add a bet with the estimate of the attacker's choosing for this validator..
                # ..continue to the next one so we can keep trying
                except:
                    continue

                # If new bet successful...

                # ...record that progress was made
                progress_made = True


                # ...remove the sender from the attack surface...
                self.attack_surface.pop(v)

                # ...we would like to move the validator from "voting against" to "voting with"...
                to_remove_from_voting_against_attacker.add(v)  # ...but actually we can only mark them for later removal because we are currently iterating over "voting_against"
                self.voting_with_attacker.add(v)  # ...however we can add them to "voting_with"

                # ...record that we made 2X "weights[v]" of progress...
                self.weight_of_victim_estimate -= WEIGHTS[v]
                self.weight_of_target_estimate += WEIGHTS[v]
                self.update_attack_delta()

                # ...update our latest bets...
                self.latest_bets[v] = new_bet

                # ...make this bet "viewable" to all validators who are still voting against the attacker...
                for v2 in self.voting_against_attacker.difference(to_remove_from_voting_against_attacker):
                    self.validator_models[v2].make_viewable(new_bet)

                # ...updating the attack view
                self.attack_view.add_bet(new_bet)

                # ...add a log of our operations
                self.operations_log.append(["added valid bet for a validator voting against the attacker", str(new_bet)])

                if self.is_attack_complete():
                    return True, self.operations_log

            # now that the attack loop is done, we can remove the validators who made new bets from the "voting_against" set
            self.voting_against_attacker.difference_update(to_remove_from_voting_against_attacker)

            # if the attack was complete, it should have been captured at the end of the for loops for phases 1 or 2 of the network attack!
            assert not self.is_attack_complete(), "...expected attack to be ongoing, at this point"

        # if ever we exist the while(progress_made) loop with progress_made == False rather than a return value, then the attack has failed
        assert not progress_made, "...expected to exit loop only when progress is not made"
        return False, self.operations_log



# validators have...
# views...
# ability to make new latest bet w esimate in the view
# ability to make new latest bet w given estimate or throwing
# ability to "decide" on a value of the consensus

class Validator:
    def __init__(self, name):
        self.name = name
        self.view = View(set())
        self.latest_estimate = None
        self.latest_bet = None
        self.latest_observed_bets = dict.fromkeys(VALIDATOR_NAMES, None)
        self.decided = False
        self.my_latest_bet = None

    def decide_if_safe(self):

        print "entering decide if safe!"
        print "self.latest_estimate", self.latest_estimate
        if self.latest_estimate is None:
            return False

        # print str(self.view)
        adversary = Adversary(self.view, self.latest_estimate)

        print "about to conduct ideal attack"
        unsafe, _ = adversary.ideal_network_attack()

        print "are we safe?, ", not unsafe

        self.decided = not unsafe
        return not unsafe

    def get_latest_estimate(self):
        scores = dict.fromkeys(ESTIMATE_SPACE, 0)
        for v in VALIDATOR_NAMES:
            if self.latest_observed_bets[v] is not None:
                scores[self.latest_observed_bets[v].estimate] += WEIGHTS[v]

        max_score = 0
        max_score_estimate = None
        for e in ESTIMATE_SPACE:
            if max_score == 0:
                max_score = scores[e]
                max_score_estimate = e
                continue

            if scores[e] > max_score:
                max_score = scores[e]
                max_score_estimate = e

        if max_score == 0:
            raise Exception("expected non-empty latest_observed_bets")
        return max_score_estimate

    def make_bet_with_null_justification(self, estimate):
        assert len(self.view.bets) == 0 and self.my_latest_bet is None, "...cannot make null justification on a non-empty view"
        self.my_latest_bet = Bet(estimate, set(), self.name)
        self.view.bets.add(self.my_latest_bet)
        self.latest_observed_bets[self.name] = self.my_latest_bet
        return self.my_latest_bet

    def make_new_latest_bet(self):

        if len(self.view.bets) == 0 and self.my_latest_bet is None:
            self.latest_estimate = r.choice(tuple(ESTIMATE_SPACE))
            self.my_latest_bet = self.make_bet_with_null_justification(self.latest_estimate)
            self.view.bets.add(self.my_latest_bet)
            self.latest_observed_bets[self.name] = self.my_latest_bet

            self.decide_if_safe()
            return self.my_latest_bet

        estimate = self.get_latest_estimate()
        justification = set()
        for v in VALIDATOR_NAMES:
            if self.latest_observed_bets[v] is not None:
                justification.add(self.latest_observed_bets[v])
        sender = self.name

        self.my_latest_bet = Bet(estimate, justification, sender)
        self.latest_estimate = estimate
        self.view.bets.add(self.my_latest_bet)
        self.latest_observed_bets[self.name] = self.my_latest_bet

        self.decide_if_safe()
        return self.my_latest_bet


    def update_view_and_latest_bets(self):

        to_remove_from_view = []
        for b in self.view.bets:
            if self.latest_observed_bets[b.sender] is None:
                self.latest_observed_bets[b.sender] = b
                continue

            # ...is_dependency is not defined for self.latest_observed_bets[b.sender] == None
            if self.latest_observed_bets[b.sender].is_dependency(b):
                self.latest_observed_bets[b.sender] = b
                continue

            assert b == self.latest_observed_bets[b.sender] or b.is_dependency(self.latest_observed_bets[b.sender]), "...did not expect any equivocating nodes!"
            to_remove_from_view.append(b)

        self.view.bets.difference_update(to_remove_from_view)

    def show_single_bet(self, bet):
        if not self.decided:
            self.view.add_bet(bet)
            self.update_view_and_latest_bets()
        else:
            print "unable to show bet to decided node"

    def show_set_of_bets(self, bets):
        if not self.decided:
            for bet in bets:
                self.view.add_bet(bet)
            self.update_view_and_latest_bets()
        else:
            print "unable to show bet to decided node"




class Network:
    def __init__(self):
        self.validators = dict()
        for v in VALIDATOR_NAMES:
            self.validators[v] = Validator(v)
        self.global_view = set()

    def propagate_bet_to_validator(self, bet, validator_name):
        assert bet in self.global_view, "...expected only to propagate bets from the global view"
        self.validators[validator_name].show_single_bet(bet)


    def get_bet_from_validator(self, validator_name):
        assert validator_name in VALIDATOR_NAMES, "...expected a known validator"

        if self.validators[validator_name].decided:
            return True

        new_bet = self.validators[validator_name].make_new_latest_bet()
        self.global_view.add(new_bet)


    def random_propagation_and_bet(self):

        destination = r.choice(tuple(VALIDATOR_NAMES))
        if len(self.global_view) == 0:
            self.get_bet_from_validator(destination)
        else:
            bet = r.choice(tuple(self.global_view))
            self.propagate_bet_to_validator(bet, destination)
            self.get_bet_from_validator(destination)

    # def let_validator_push

    def random_initialization(self):
        for v in VALIDATOR_NAMES:
            self.get_bet_from_validator(v)

        print str(self.global_view)

    def report(self, decided):
        View(self.global_view).plot_view(decided)




network = Network()
network.random_initialization()

print "WEIGHTS", WEIGHTS

decided = dict.fromkeys(VALIDATOR_NAMES, 0)

while(True):


    network.report(decided)

    l = []

    for i in xrange(NUM_VALIDATORS):
        l.append(network.validators[i].my_latest_bet)

    for i in xrange(NUM_VALIDATORS):
        for j in xrange(NUM_VALIDATORS):
            if i != j and (r.randint(0, 4) == 0):
                network.propagate_bet_to_validator(l[j], i)

        if not decided[i]:
            network.get_bet_from_validator(i)
            for v in VALIDATOR_NAMES:
                decided[v] = network.validators[v].decided
            # print "decided:", decided



'''
EXAMPLE 1
'''

WEIGHTS[0] = 3
WEIGHTS[1] = 4
WEIGHTS[2] = 5


for i in xrange(0):


    if i == 0:
        a = Bet(1, [], 0)
        b = Bet(0, [], 1)
        c = Bet(1, [], 2)

        view = View(set([a, b, c]))

        adversary = Adversary(view, 1)
        success, attack_log = adversary.ideal_network_attack()

    if i == 1:
        a = Bet(1, [], 0)
        b = Bet(0, [], 1)
        c = Bet(1, [], 2)
        b2 = Bet(1, [a, b, c], 1)

        view = View(set([a, b, c, b2]))

        adversary = Adversary(view, 1)
        success, attack_log = adversary.ideal_network_attack()


    if i == 2:
        a = Bet(1, [], 0)
        b = Bet(1, [], 1)
        c = Bet(1, [], 2)

        view = View(set([a, b, c]))

        adversary = Adversary(view, 1)
        success, attack_log = adversary.ideal_network_attack()

    if i == 3:

        a = Bet(1, [], 0)
        b = Bet(1, [], 1)
        c = Bet(1, [], 2)

        a1 = Bet(1, [a, b, c], 0)
        b1 = Bet(1, [a, b, c], 1)
        c1 = Bet(1, [a, b, c], 2)


        view = View(set([a, b, c, a1, b1, c1]))

        adversary = Adversary(view, 1)
        success, attack_log = adversary.ideal_network_attack()


    print "-------------------------------Victim View--------------------------------------------"
    print str(view)

    if success:
        print "Ideal network was attack successful..."
    else:
        print "Ideal network was attack unsuccessful..."

    if success:
        print "...with the following operations_log:"
        for l in attack_log:
            print l

        print "-------------------------------Post-attack View-----------------------------------"
        print str(adversary.attack_view)


    view.plot_view()
    adversary.attack_view.plot_view()
