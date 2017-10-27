"""The adversary oracle module ... """
from casper.safety_oracles.adversary_models.model_bet import ModelBet
from casper.safety_oracles.adversary_models.adversary import Adversary
from casper.safety_oracles.abstract_oracle import AbstractOracle
import casper.utils as utils


class AdversaryOracle(AbstractOracle):
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
        for validator in self.validator_set:
            # ... if nothing is seen from validator, assume the worst ...
            if validator not in self.view.latest_messages:
                recent_messages[validator] = ModelBet(AdversaryOracle.ADV_ESTIMATE, validator)
                viewables[validator] = dict()

            # ... or if their most recent messages conflicts w/ estimate,
            # again working with adversary.
            elif self.candidate_estimate.conflicts_with(self.view.latest_messages[validator]):
                recent_messages[validator] = ModelBet(AdversaryOracle.ADV_ESTIMATE, validator)
                viewables[validator] = dict()

            else:
                # Sanity check!
                assert not self.candidate_estimate.conflicts_with(self.view.latest_messages[validator])

                # These are the validators who are voting with the candidate_estimate.
                recent_messages[validator] = ModelBet(AdversaryOracle.CAN_ESTIMATE, validator)
                viewables[validator] = dict()
                # now construct the messages that they can see from other validators
                for val2 in self.validator_set:
                    # if they have seen nothing from some validator, assume the worst
                    # NOTE: This may not be necessary, might be possible to do a free
                    # block check here? see issue #44
                    if val2 not in self.view.latest_messages[validator].justification.latest_messages:
                        viewables[validator][val2] = ModelBet(AdversaryOracle.ADV_ESTIMATE, val2)
                        continue

                    # If they have seen something from other validators, do a free block check
                    # If there is a free block, assume they will see that (side-effects free!)
                    val2_msg_in_v_view = self.view.latest_messages[validator].justification.latest_messages[val2]
                    if utils.exists_free_message(self.candidate_estimate,
                                                 val2, val2_msg_in_v_view.sequence_number, self.view):
                        viewables[validator][val2] = ModelBet(AdversaryOracle.ADV_ESTIMATE, val2)
                    else:
                        viewables[validator][val2] = ModelBet(AdversaryOracle.CAN_ESTIMATE, val2)

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
