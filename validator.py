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
        assert (len(self.view.bets) == 0 and
                self.my_latest_bet is None), "...cannot make null justification on a non-empty view"
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

            assert (b == self.latest_observed_bets[b.sender] or
                    b.is_dependency(self.latest_observed_bets[b.sender])), "...did not expect any equivocating nodes!"
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
