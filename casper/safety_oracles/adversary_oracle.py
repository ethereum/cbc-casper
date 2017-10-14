"""The adversary oracle module ... """
from casper.safety_oracles.adversary_models.model_bet import ModelBet
from casper.safety_oracles.adversary_models.adversary import Adversary
import casper.utils as utils


class AdversaryOracle:
    """Runs an lower bound adversary to check safety on some estimate."""

    # We say candidate_estimate is 0, other is 1
    CAN_ESTIMATE = 0
    ADV_ESTIMATE = 1

    def __init__(self, candidate_estimate, view, validator_set):
        if candidate_estimate is None:
            raise Exception("cannot decide if safe without an estimate")

        self.candidate_estimate = candidate_estimate
        self.view = view
        self.validator_set = validator_set

    def get_recent_messages_and_viewables(self):
        """Converts some current view to binary to make reasoning about viewables easier."""

        recent_messages = dict()
        viewables = dict()

        # For some validator ...
        for v in self.validator_set:
            # ... if nothing is seen from validator, assume the worst ...
            if v not in self.view.latest_messages:
                recent_messages[v] = ModelBet(AdversaryOracle.ADV_ESTIMATE, v)
                viewables[v] = dict()

            # ... or if their most recent messages conflicts w/ estimate,
            # again working with adversary.
            elif utils.are_conflicting_estimates(self.candidate_estimate, self.view.latest_messages[v]):
                recent_messages[v] = ModelBet(AdversaryOracle.ADV_ESTIMATE, v)
                viewables[v] = dict()

            else:
                # Sanity check!
                assert not utils.are_conflicting_estimates(self.candidate_estimate, self.view.latest_messages[v])

                # These are the validators who are voting with the candidate_estimate.
                recent_messages[v] = ModelBet(AdversaryOracle.CAN_ESTIMATE, v)
                viewables[v] = dict()
                # now construct the messages that they can see from other validators
                for v2 in self.validator_set:
                    # if they have seen nothing from some validator, assume the worst
                    # NOTE: This may not be necessary, might be possible to do a free
                    # block check here? see issue #44
                    if v2 not in self.view.latest_messages[v].justification.latest_messages:
                        viewables[v][v2] = ModelBet(AdversaryOracle.ADV_ESTIMATE, v2)
                        continue

                    # If they have seen something from other validators, do a free block check
                    # If there is a free block, assume they will see that (side-effects free!)
                    v2_msg_in_v_view = self.view.latest_messages[v].justification.latest_messages[v2]
                    if utils.exists_free_message(self.candidate_estimate, v2, v2_msg_in_v_view.sequence_number, self.view):
                        viewables[v][v2] = ModelBet(AdversaryOracle.ADV_ESTIMATE, v2)
                    else:
                        viewables[v][v2] = ModelBet(AdversaryOracle.CAN_ESTIMATE, v2)

        return recent_messages, viewables

    def check_estimate_safety(self):
        """Check the safety of the estimate."""

        recent_messages, viewables = self.get_recent_messages_and_viewables()

        adversary = Adversary(self.CAN_ESTIMATE, recent_messages, viewables, self.validator_set)

        attack_success, _, _ = adversary.ideal_network_attack()

        if not attack_success:
            # Because the adversary tells us nothing about validators that need to equivocate,
            # assume the worst.
            return min(self.validator_set.validator_weights()), 1
        else:
            return 0, 0
