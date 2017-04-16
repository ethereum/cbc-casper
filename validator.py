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
        self.latest_observed_bets = dict()
        self.vicarious_latest_bets = dict()
        self.viewables = dict()
        for v in VALIDATOR_NAMES:
            self.vicarious_latest_bets[v] = dict()
            self.viewables[v] = dict()
        self.decided = False
        self.my_latest_bet = None
        self.my_latest_estimate = None

        # this will store the latest bets seen from validators, for each estimate
        self.lastest_bets_with_estimate = dict()
        for e in ESTIMATE_SPACE:
            self.lastest_bets_with_estimate[e] = dict()

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
    def get_viewables(self):
        # if this validator has no latest bets in the view, then we store...

        viewables = dict()
        for v in VALIDATOR_NAMES:
            viewables[v] = dict()

        for w in VALIDATOR_NAMES:
            if w not in self.latest_observed_bets:

                # for validators without anything in their view, any bets are later bets are viewable bets!
                # ...so we add them all in!
                for v in self.lastest_bets_with_estimate[1 - self.my_latest_estimate].keys():
                    viewables[w][v] = self.lastest_bets_with_estimate[1 - self.my_latest_estimate][v]

            # if we do have a latest bet from this validator, then...
            else:
                assert isinstance(self.latest_observed_bets[w], Bet), "...expected my_latest_bet to be a bet or the empty set"

                # then all bets that are causally after these bets are viewable by this validator

                for v in self.lastest_bets_with_estimate[1 - self.my_latest_estimate].keys():
                    if v not in self.vicarious_latest_bets[w].keys():
                        viewables[w][v] = self.lastest_bets_with_estimate[1 - self.my_latest_estimate][v]
                        continue

                    if self.vicarious_latest_bets[w][v].sequence_number < self.lastest_bets_with_estimate[1 - self.my_latest_estimate][v].sequence_number:
                        viewables[w][v] = self.lastest_bets_with_estimate[1 - self.my_latest_estimate][v]

        return viewables

    @profile
    def decide_if_safe(self):

        print "entering decide if safe!"
        print "self.my_latest_estimate", self.my_latest_estimate
        if self.get_latest_estimate() is None:
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

        self.viewables = self.get_viewables()

        adversary = Adversary(self.my_latest_estimate, copy.deepcopy(self.latest_observed_bets), copy.deepcopy(self.vicarious_latest_bets), copy.deepcopy(self.viewables))

        print "about to conduct ideal attack"
        unsafe, _, _ = adversary.ideal_network_attack()

        print "are we safe?, ", not unsafe

        self.decided = not unsafe
        return not unsafe

    def make_bet_with_null_justification(self, estimate):
        assert (len(self.view.bets) == 0 and
                self.my_latest_bet is None), "...cannot make null justification on a non-empty view"
        self.my_latest_bet = Bet(estimate, dict(), self.name)
        self.view.add_bet(self.my_latest_bet)
        self.latest_observed_bets[self.name] = self.my_latest_bet
        return self.my_latest_bet

    def make_new_latest_bet(self):

        if len(self.view.bets) == 0 and self.my_latest_bet is None:
            estimate = r.choice(tuple(ESTIMATE_SPACE))
            self.my_latest_bet = self.make_bet_with_null_justification(estimate)
            self.view.add_bet(self.my_latest_bet)

            self.my_latest_estimate = estimate
            return self.my_latest_bet

        estimate = self.get_latest_estimate()
        justification = self.latest_observed_bets
        sender = self.name

        self.my_latest_bet = Bet(estimate, justification, sender)
        # self.my_latest_bet.make_redundancy_free()
        self.my_latest_estimate = estimate
        self.view.add_bet(self.my_latest_bet)
        self.latest_observed_bets[self.name] = self.my_latest_bet

        return self.my_latest_bet

    @profile
    def update_view_and_latest_bets(self, showed_bets):

        '''
        PART 1 - updating latest bets
        '''

        sequence_numbers = dict()
        for v in self.latest_observed_bets:
            sequence_numbers[v] = self.latest_observed_bets[v].sequence_number

        newly_discovered_bets = View(showed_bets).get_extension_up_to_sequence_numbers(sequence_numbers)

        # updating latest bets..
        for b in newly_discovered_bets:

            if b.sender not in self.latest_observed_bets:
                self.latest_observed_bets[b.sender] = b
                self.lastest_bets_with_estimate[b.estimate][b.sender] = b
                continue

            if self.latest_observed_bets[b.sender].sequence_number < b.sequence_number:
                self.latest_observed_bets[b.sender] = b
                self.lastest_bets_with_estimate[b.estimate][b.sender] = b
                continue

            if b.sender not in self.lastest_bets_with_estimate[b.estimate]:
                self.lastest_bets_with_estimate[b.estimate][b.sender] = b
                continue

            if self.lastest_bets_with_estimate[b.estimate][b.sender].sequence_number < b.sequence_number:
                self.lastest_bets_with_estimate[b.estimate][b.sender] = b

            assert (b == self.latest_observed_bets[b.sender] or
                    b.is_dependency_from_same_validator(self.latest_observed_bets[b.sender])), "...did not expect any equivocating nodes!"

        '''
        PART 2 - updating vicarious latest bets
        '''

        # updating vicarious_latest_bets for validator v, for all v..
        for v in self.latest_observed_bets:
            self.vicarious_latest_bets[v] = self.latest_observed_bets[v].justification

    @profile
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
