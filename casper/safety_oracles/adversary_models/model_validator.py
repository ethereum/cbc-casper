"""The model validator module ... """
import casper.safety_oracles.adversary_models.model_utils as model_utils
from casper.safety_oracles.adversary_models.model_bet import (
    ModelBet
)


class ModelValidator(object):
    """Simulates a model validator."""

    def __init__(self, validator, my_latest_bet, latest_bets, target_estimate):
        self.model_of = validator
        self.weight = validator.weight

        self.my_latest_bet = my_latest_bet
        self.target_estimate = target_estimate

        self.latest_observed_bets = latest_bets

    def my_estimate(self):
        """Model validators use their latest_observed_bets to calculate an estimate."""
        return model_utils.get_estimate_from_latest_messages(self.latest_observed_bets,
                                                             self.target_estimate)

    def show(self, bet):
        """This method makes a bet viewable to the model validator."""

        assert isinstance(bet, ModelBet), "expected a bet!"
        assert bet.estimate == self.target_estimate, "should only show bets on the target_estimate!"

        self.latest_observed_bets[bet.sender] = bet


    def make_new_latest_bet(self):
        """This function attempts to make a new latest bet for
        this validator (self) with a given estimate."""

        if self.my_latest_bet.estimate == self.target_estimate:
            return True, self.my_latest_bet

        if self.my_estimate() == self.target_estimate:
            self.my_latest_bet = ModelBet(self.target_estimate, self.model_of)
            return True, self.my_latest_bet

        return False, None
