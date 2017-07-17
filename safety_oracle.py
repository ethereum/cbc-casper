from settings import VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS
from bet import Bet
from adversary import Adversary

import copy


class Safety_Oracle:

    def __init__(self, candidate_estimate, view):
        self.candidate_estimate = candidate_estimate
        self.latest_observed_bets = view.latest_bets

    # This method returns a map estimates -> validator -> bet with estimate
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
                for v in lastest_bets_with_estimate[1 - self.candidate_estimate].keys():
                    viewables[w][v] = lastest_bets_with_estimate[1 - self.candidate_estimate][v]

            # if we do have a latest bet from this validator, then...
            else:
                assert isinstance(self.latest_observed_bets[w], Bet), "...expected my_latest_bet to be a bet or the empty set"

                # then all bets that are causally after these bets are viewable by this validator

                for v in lastest_bets_with_estimate[1 - self.candidate_estimate].keys():
                    if v not in self.latest_observed_bets[w].justification.latest_bets.keys():
                        viewables[w][v] = lastest_bets_with_estimate[1 - self.candidate_estimate][v]
                        continue

                    if self.latest_observed_bets[w].justification.latest_bets[v].sequence_number < lastest_bets_with_estimate[1 - self.candidate_estimate][v].sequence_number:
                        viewables[w][v] = lastest_bets_with_estimate[1 - self.candidate_estimate][v]

        return viewables

    @profile
    def check_estimate_safety(self):

        if self.candidate_estimate is None:
            raise Exception("cannot decide if safe without an estimate")

        viewables = self.get_viewables()

        latest_bets_copy = copy.deepcopy(self.latest_observed_bets)
        viewables_copy = copy.deepcopy(viewables)

        adversary = Adversary(self.candidate_estimate, latest_bets_copy, viewables_copy)

        unsafe, _, _ = adversary.ideal_network_attack()

        return not unsafe
