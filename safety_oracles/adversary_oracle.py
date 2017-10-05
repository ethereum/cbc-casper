import settings as s
from adversary_models.model_bet import Model_Bet
from adversary_models.adversary import Adversary
import utils


class Adversary_Oracle:

    def __init__(self, candidate_estimate, view):
        if candidate_estimate is None:
            raise Exception("cannot decide if safe without an estimate")

        self.candidate_estimate = candidate_estimate
        self.view = view

        #TODO: make these class level (static :) )
        # by convention, we say candidate_estimate is 0, other is 1
        self.CAN_ESTIMATE = 0
        self.ADV_ESTIMATE = 1


    # we essentially convert to a binary system - as it is an lower bound,
    # and is much easier to reason about
    def get_recent_messages_and_viewables(self):

        recent_messages = dict()
        viewables = dict()

        for v in s.VALIDATOR_NAMES:
            if v not in self.view.latest_messages:
                recent_messages[v] = Model_Bet(self.ADV_ESTIMATE, v)
                viewables[v] = dict()

            elif utils.are_conflicting_estimates(self.candidate_estimate, self.view.latest_messages[v]):
                recent_messages[v] = Model_Bet(self.ADV_ESTIMATE, v)
                viewables[v] = dict()

            else:

                assert not utils.are_conflicting_estimates(self.candidate_estimate, self.view.latest_messages[v])

                # these are the validators who are voting with the candidate_estimate
                recent_messages[v] = Model_Bet(self.CAN_ESTIMATE, v)
                viewables[v] = dict()
                # for the rest of of the validators, consider those that
                for v2 in s.VALIDATOR_NAMES:
                    if v2 not in self.view.latest_messages[v].justification.latest_messages:
                        viewables[v][v2] = Model_Bet(self.ADV_ESTIMATE, v2)
                        continue

                    # thsi is the one questionable bit
                    v2_msg_in_v_view = self.view.latest_messages[v].justification.latest_messages[v2]
                    if utils.exists_free_message(self.candidate_estimate, v2, v2_msg_in_v_view.sequence_number, self.view):
                        viewables[v][v2] = Model_Bet(self.ADV_ESTIMATE, v2)
                    else:
                        viewables[v][v2] = Model_Bet(self.CAN_ESTIMATE, v2)


        return recent_messages, viewables


    def check_estimate_safety(self):

        recent_messages, viewables = self.get_recent_messages_and_viewables()

        adversary = Adversary(self.CAN_ESTIMATE, recent_messages, viewables)

        attack_success, log, view = adversary.ideal_network_attack()

        if not attack_success:
            return min(s.WEIGHTS.values()), 1
        else:
            return 0, 0
