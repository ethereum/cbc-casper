from settings import VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS
from bet import Bet
from view import View
from adversary import Adversary
import random as r

r.seed()

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
        self.latest_observed_bets = dict()
        self.vicarious_latest_bets = dict()
        for v in VALIDATOR_NAMES:
            self.vicarious_latest_bets[v] = dict()
        self.decided = False
        self.my_latest_bet = None

        self.already_committed_view = View(set())

    def decide_if_safe(self):

        print "entering decide if safe!"
        print "self.latest_estimate", self.latest_estimate
        if self.latest_estimate is None:
            raise Exception("cannot decide if safe without an estimate")

        # print str(self.view)
        # OUR GOAL IS TO DO ALL OF THE GET_LATEST_BETS AND GET_EXTENSION CALCULATIONS DONE IN THE ADVERSARY IN THE VALIDATOR INSTEAD
        adversary = Adversary(self.view, self.latest_estimate, self.latest_observed_bets, self.vicarious_latest_bets)

        print "about to conduct ideal attack"
        unsafe, _ = adversary.ideal_network_attack()

        print "are we safe?, ", not unsafe

        self.decided = not unsafe
        return not unsafe

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

    def make_bet_with_null_justification(self, estimate):
        assert (len(self.view.bets) == 0 and
                self.my_latest_bet is None), "...cannot make null justification on a non-empty view"
        self.my_latest_bet = Bet(estimate, set(), self.name)
        self.view.add_bet(self.my_latest_bet)
        self.latest_observed_bets[self.name] = self.my_latest_bet
        return self.my_latest_bet

    def make_new_latest_bet(self):

        if len(self.view.bets) == 0 and self.my_latest_bet is None:
            self.latest_estimate = r.choice(tuple(ESTIMATE_SPACE))
            self.my_latest_bet = self.make_bet_with_null_justification(self.latest_estimate)
            self.view.add_bet(self.my_latest_bet)
            self.latest_observed_bets[self.name] = self.my_latest_bet

            self.decide_if_safe()
            return self.my_latest_bet

        estimate = self.get_latest_estimate()
        justification = set()
        for v in VALIDATOR_NAMES:
            if v in self.latest_observed_bets:
                justification.add(self.latest_observed_bets[v])

        to_be_removed = set()
        for j in justification:
            if j in self.already_committed_view.bets:
                to_be_removed.add(j)

        justification.difference_update(to_be_removed)

        self.already_committed_view.add_view(View(justification))

        sender = self.name

        self.my_latest_bet = Bet(estimate, justification, sender)
        self.latest_estimate = estimate
        self.view.add_bet(self.my_latest_bet)
        self.latest_observed_bets[self.name] = self.my_latest_bet

        self.decide_if_safe()
        return self.my_latest_bet

    @profile
    def update_view_and_latest_bets(self, showed_bets):

        to_remove_from_view = []

        # bets that this validator just now sees for the first time
        newly_discovered_bets = View(showed_bets).get_extension().difference(self.already_committed_view.bets)

        # updating latest bets..
        for b in newly_discovered_bets:

            if b.sender not in self.latest_observed_bets:
                self.latest_observed_bets[b.sender] = b
                continue

            # ...is_dependency is not defined for self.latest_observed_bets[b.sender] == None
            if self.latest_observed_bets[b.sender].is_dependency(b):
                self.latest_observed_bets[b.sender] = b
                continue

            print "b, latest_observed_bets[b.sender]", b, self.latest_observed_bets[b.sender]
            assert (b == self.latest_observed_bets[b.sender] or
                    b.is_dependency(self.latest_observed_bets[b.sender])), "...did not expect any equivocating nodes!"

            to_remove_from_view.append(b)

        # updating vicarious_latest_bets..
        for b in newly_discovered_bets:
            for v in self.latest_observed_bets:
                if b.sender != v and b.is_dependency(self.latest_observed_bets[v]):
                    if b.sender not in self.vicarious_latest_bets[v] or self.vicarious_latest_bets[v][b.sender].is_dependency(b):
                        self.vicarious_latest_bets[v][b.sender] = b

        self.view.remove_bets(to_remove_from_view)

    def show_single_bet(self, bet):
        if not self.decided:
            self.view.add_bet(bet)
            self.update_view_and_latest_bets(set([bet]))
        else:
            print "unable to show bet to decided node"

    def show_set_of_bets(self, bets):
        if not self.decided:
            for bet in bets:
                self.view.add_bet(bet)
            self.update_view_and_latest_bets(bets)
        else:
            print "unable to show bet to decided node"
