from settings import VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS
from bet import Bet
from adversary import Adversary

import copy


class Safety_Oracle:

    def __init__(self, candidate_estimate, view):
        self.candidate_estimate = candidate_estimate
        self.latest_observed_messages = view.latest_messages

    # This method returns a map estimates -> validator -> bet with estimate
    @profile
    def get_latest_messages_with_estimate(self):

        lastest_messages_with_estimate = dict()
        for e in ESTIMATE_SPACE:
            lastest_messages_with_estimate[e] = dict()

        for v in self.latest_observed_messages:
            lastest_messages_with_estimate[self.latest_observed_messages[v].estimate][v] = self.latest_observed_messages[v]

        return lastest_messages_with_estimate

    @profile
    def get_viewables(self):
        # if this validator has no latest bets in the view, then we store...

        lastest_messages_with_estimate = self.get_latest_messages_with_estimate()

        viewables = dict()
        for v in VALIDATOR_NAMES:
            viewables[v] = dict()

        for w in VALIDATOR_NAMES:
            if w not in self.latest_observed_messages:

                # for validators without anything in their view, any bets are later bets are viewable bets!
                # ...so we add them all in!
                for v in lastest_messages_with_estimate[1 - self.candidate_estimate].keys():
                    viewables[w][v] = lastest_messages_with_estimate[1 - self.candidate_estimate][v]

            # if we do have a latest bet from this validator, then...
            else:
                assert isinstance(self.latest_observed_messages[w], Bet), "...expected my_latest_bet to be a bet or the empty set"

                # then all bets that are causally after these bets are viewable by this validator

                for v in lastest_messages_with_estimate[1 - self.candidate_estimate].keys():
                    if v not in self.latest_observed_messages[w].justification.latest_messages.keys():
                        viewables[w][v] = lastest_messages_with_estimate[1 - self.candidate_estimate][v]
                        continue

                    if self.latest_observed_messages[w].justification.latest_messages[v].sequence_number < lastest_messages_with_estimate[1 - self.candidate_estimate][v].sequence_number:
                        viewables[w][v] = lastest_messages_with_estimate[1 - self.candidate_estimate][v]

        return viewables

    @profile
    def check_estimate_safety(self):

        if self.candidate_estimate is None:
            raise Exception("cannot decide if safe without an estimate")

        viewables = self.get_viewables()

        latest_messages_copy = copy.deepcopy(self.latest_observed_messages)
        viewables_copy = copy.deepcopy(viewables)

        adversary = Adversary(self.candidate_estimate, latest_messages_copy, viewables_copy)

        unsafe, _, _ = adversary.ideal_network_attack()

        return not unsafe
