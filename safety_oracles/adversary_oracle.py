import settings as s
from adversary_models.model_bet import ModelBet
from adversary_models.adversary import Adversary
import utils


class AdversaryOracle:
    # we say candidate_estimate is 0, other is 1
    CAN_ESTIMATE = 0
    ADV_ESTIMATE = 1

    def __init__(self, candidate_estimate, view):
        if candidate_estimate is None:
            raise Exception("cannot decide if safe without an estimate")

        self.candidate_estimate = candidate_estimate
        self.view = view


    # "converts" the current view to binary before running the safety oracle
    # makes reasoning about best viewables much easier.
    # if, for two validators,
    def get_recent_messages_and_viewables(self):

        recent_messages = dict()
        viewables = dict()

        for v in s.VALIDATOR_NAMES:
            # if nothing is seen from validator, assume the worst
            if v not in self.view.latest_messages:
                recent_messages[v] = ModelBet(AdversaryOracle.ADV_ESTIMATE, v)
                viewables[v] = dict()

            # or if their most recent messages conflicts w/ estimate, again working with adversary
            elif utils.are_conflicting_estimates(self.candidate_estimate, self.view.latest_messages[v]):
                recent_messages[v] = ModelBet(AdversaryOracle.ADV_ESTIMATE, v)
                viewables[v] = dict()

            else:
                # sanity check
                assert not utils.are_conflicting_estimates(self.candidate_estimate, self.view.latest_messages[v])

                # these are the validators who are voting with the candidate_estimate
                recent_messages[v] = ModelBet(AdversaryOracle.CAN_ESTIMATE, v)
                viewables[v] = dict()
                # now construct the messages that they can see from other validators
                for v2 in s.VALIDATOR_NAMES:
                    # if they have seen nothing from some validator, assume the worst
                    # TODO: figure out if this is necessary. might be possible to do a free block check here?
                    if v2 not in self.view.latest_messages[v].justification.latest_messages:
                        viewables[v][v2] = ModelBet(AdversaryOracle.ADV_ESTIMATE, v2)
                        continue

                    # if they have seen something from other validators, do a free block check
                    # if there is a free block, assume they will see that (side-effects free!)
                    v2_msg_in_v_view = self.view.latest_messages[v].justification.latest_messages[v2]
                    if utils.exists_free_message(self.candidate_estimate, v2, v2_msg_in_v_view.sequence_number, self.view):
                        viewables[v][v2] = ModelBet(AdversaryOracle.ADV_ESTIMATE, v2)
                    else:
                        viewables[v][v2] = ModelBet(AdversaryOracle.CAN_ESTIMATE, v2)


        return recent_messages, viewables


    def check_estimate_safety(self):

        recent_messages, viewables = self.get_recent_messages_and_viewables()

        adversary = Adversary(self.CAN_ESTIMATE, recent_messages, viewables)

        attack_success, log, view = adversary.ideal_network_attack()

        if not attack_success:
            # Because the adversary tells us nothing about validators that need to equivocate,
            # assume the worst. 
            return min(s.WEIGHTS.values()), 1
        else:
            return 0, 0
