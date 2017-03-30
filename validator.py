from settings import VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS
from bet import Bet
from view import View
from adversary import Adversary
import copy
import random as r

r.seed()

# validators have...
# views...
# ability to make new latest bet w esimate in the view
# ability to make new latest bet w given estimate or throwing
# ability to "decide" on a value of the consensus

REPORT = False


class Validator:
    @profile
    def __init__(self, name):
        self.name = name
        self.view = View(set())
        self.latest_estimate = None
        self.latest_observed_bets = dict()
        self.vicarious_latest_bets = dict()
        for v in VALIDATOR_NAMES:
            self.vicarious_latest_bets[v] = dict()
        self.decided = False
        self.my_latest_bet = None

    @profile
    def decide_if_safe(self):

        print "entering decide if safe!"
        print "self.latest_estimate", self.latest_estimate
        if self.latest_estimate is None:
            raise Exception("cannot decide if safe without an estimate")

        if REPORT:
            lb = View([])
            for v in VALIDATOR_NAMES:
                if v in self.latest_observed_bets:
                    lb.add_bet(self.latest_observed_bets[v])
            print "ADVERSARY IS BEING FED THIS AS LATEST BETS:"
            lb.plot_view(lb.bets, 'yellow')

            vic_lb = View([])
            for v in VALIDATOR_NAMES:
                for w in VALIDATOR_NAMES:
                    if w in self.vicarious_latest_bets[v]:
                        vic_lb.add_bet(self.vicarious_latest_bets[v][w])
            print "ADVERSARY IS BEING FED THIS AS VICARIOUS LATEST BETS:"
            vic_lb.plot_view(vic_lb.bets, 'yellow')

        adversary = Adversary(self.view, self.latest_estimate, copy.deepcopy(self.latest_observed_bets), copy.deepcopy(self.vicarious_latest_bets))

        print "about to conduct ideal attack"
        unsafe, _ = adversary.ideal_network_attack()

        print "are we safe?, ", not unsafe

        self.decided = not unsafe
        return not unsafe

    @profile
    def get_latest_estimate(self):
        scores = dict.fromkeys(ESTIMATE_SPACE, 0)
        for v in VALIDATOR_NAMES:
            if v in self.latest_observed_bets:
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

    @profile
    def make_bet_with_null_justification(self, estimate):
        assert (len(self.view.bets) == 0 and
                self.my_latest_bet is None), "...cannot make null justification on a non-empty view"
        self.my_latest_bet = Bet(estimate, set(), self.name)
        self.view.add_bet(self.my_latest_bet)
        self.latest_observed_bets[self.name] = self.my_latest_bet
        return self.my_latest_bet

    @profile
    def make_new_latest_bet(self):

        if len(self.view.bets) == 0 and self.my_latest_bet is None:
            self.latest_estimate = r.choice(tuple(ESTIMATE_SPACE))
            self.my_latest_bet = self.make_bet_with_null_justification(self.latest_estimate)
            self.view.add_bet(self.my_latest_bet)

            self.decide_if_safe()
            return self.my_latest_bet

        if self.my_latest_bet is None:
            already_committed_view = View(set())
        else:
            already_committed_view = View(View(self.my_latest_bet.justification).get_extension())

        estimate = self.get_latest_estimate()
        justification = set()
        for v in VALIDATOR_NAMES:
            if v in self.latest_observed_bets:
                justification.add(self.latest_observed_bets[v])

        to_be_removed = set()
        for j in justification:
            if j in already_committed_view.bets:
                to_be_removed.add(j)

        justification.difference_update(to_be_removed)

        sender = self.name

        self.my_latest_bet = Bet(estimate, justification, sender)
        self.my_latest_bet.make_redundancy_free()

        self.latest_estimate = estimate
        self.view.add_bet(self.my_latest_bet)
        self.latest_observed_bets[self.name] = self.my_latest_bet

        self.decide_if_safe()
        return self.my_latest_bet

    @profile
    def update_view_and_latest_bets(self, showed_bets):

        to_remove_from_view = []

        '''
        PART 1 - updating latest bets
        '''

        if self.my_latest_bet is None:
            already_committed_view = View(set())
        else:
            already_committed_view = View(View(self.my_latest_bet.justification).get_extension())

        # bets that this validator just now sees for the first time
        newly_discovered_bets = View(showed_bets).get_extension().difference(already_committed_view.bets)

        # updating latest bets..
        for b in newly_discovered_bets:

            if b.sender not in self.latest_observed_bets:
                self.latest_observed_bets[b.sender] = b
                continue

            # ...is_dependency is not defined for self.latest_observed_bets[b.sender] == None
            if self.latest_observed_bets[b.sender].is_dependency(b):
                self.latest_observed_bets[b.sender] = b
                continue

            assert (b == self.latest_observed_bets[b.sender] or
                    b.is_dependency(self.latest_observed_bets[b.sender])), "...did not expect any equivocating nodes!"

            to_remove_from_view.append(b)

        '''
        PART 2 - updating vicarious latest bets
        '''

        # updating vicarious_latest_bets for validator v, for all v..
        for v in self.latest_observed_bets:

            previously_latest_bets = set()
            for w in self.vicarious_latest_bets[v]:
                previously_latest_bets.add(self.vicarious_latest_bets[v][w])

            previous_view = View(previously_latest_bets).get_extension()

            vicarious_newly_discovered_bets = View([self.latest_observed_bets[v]]).get_extension().difference(previous_view)

            for b in vicarious_newly_discovered_bets:
                if b.sender not in self.vicarious_latest_bets[v] or self.vicarious_latest_bets[v][b.sender].is_dependency(b):
                    self.vicarious_latest_bets[v][b.sender] = b

        self.view.remove_bets(to_remove_from_view)

    @profile
    def show_single_bet(self, bet):
        if not self.decided:
            self.view.add_bet(bet)
            self.update_view_and_latest_bets(set([bet]))
        else:
            print "unable to show bet to decided node"

    @profile
    def show_set_of_bets(self, bets):
        if not self.decided:
            for bet in bets:
                self.view.add_bet(bet)
            self.update_view_and_latest_bets(bets)
        else:
            print "unable to show bet to decided node"
