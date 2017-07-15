from settings import VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS
from bet import Bet
from adversary import Adversary

import copy
REPORT = False


class Safety_Oracle:

    def __init__(self, my_latest_estimate, latest_observed_bets, vicarious_latest_bets):
        self.my_latest_estimate = my_latest_estimate
        self.latest_observed_bets = latest_observed_bets
        self.vicarious_latest_bets = vicarious_latest_bets

    @profile
    def get_latest_bets_with_estimate(self):

        lastest_bets_with_estimate = dict()
        for e in ESTIMATE_SPACE:
            lastest_bets_with_estimate[e] = dict()

        for v in self.latest_observed_bets:
            lastest_bets_with_estimate[self.latest_observed_bets[v].estimate][v] = self.latest_observed_bets[v]

        return lastest_bets_with_estimate

    @profile
    def get_viewables(self):
        # if this validator has no latest bets in the view, then we store...

        lastest_bets_with_estimate = self.get_latest_bets_with_estimate()

        viewables = dict()
        for v in VALIDATOR_NAMES:
            viewables[v] = dict()

        for w in VALIDATOR_NAMES:
            if w not in self.latest_observed_bets:

                # for validators without anything in their view, any bets are later bets are viewable bets!
                # ...so we add them all in!
                for v in lastest_bets_with_estimate[1 - self.my_latest_estimate].keys():
                    viewables[w][v] = lastest_bets_with_estimate[1 - self.my_latest_estimate][v]

            # if we do have a latest bet from this validator, then...
            else:
                assert isinstance(self.latest_observed_bets[w], Bet), "...expected my_latest_bet to be a bet or the empty set"

                # then all bets that are causally after these bets are viewable by this validator

                print self.my_latest_estimate

                for v in lastest_bets_with_estimate[1 - self.my_latest_estimate].keys():
                    if v not in self.vicarious_latest_bets[w].keys():
                        viewables[w][v] = lastest_bets_with_estimate[1 - self.my_latest_estimate][v]
                        continue

                    if self.vicarious_latest_bets[w][v].sequence_number < lastest_bets_with_estimate[1 - self.my_latest_estimate][v].sequence_number:
                        viewables[w][v] = lastest_bets_with_estimate[1 - self.my_latest_estimate][v]

        return viewables

    @profile
    def decide_if_safe(self):

        print "entering decide if safe!"
        print "self.my_latest_estimate", self.my_latest_estimate
        if self.my_latest_estimate is None:
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

        viewables = self.get_viewables()

        latest_bets_copy = copy.deepcopy(self.latest_observed_bets)
        vicarious_bets_copy = copy.deepcopy(self.vicarious_latest_bets)
        viewables_copy = copy.deepcopy(viewables)

        adversary = Adversary(self.my_latest_estimate, latest_bets_copy, vicarious_bets_copy, viewables_copy)

        print "about to conduct ideal attack"
        unsafe, _, _ = adversary.ideal_network_attack()

        print "are we safe?, ", not unsafe

        self.decided = not unsafe
        return not unsafe
