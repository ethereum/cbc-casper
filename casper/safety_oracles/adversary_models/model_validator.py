import casper.settings as s
import casper.safety_oracles.adversary_models.model_utils as model_utils
from casper.safety_oracles.adversary_models.model_bet import (
    ModelBet
)


class ModelValidator:

    def __init__(self, validator_name, my_latest_bet, latest_bets, target_estimate):

        assert validator_name in s.VALIDATOR_NAMES, "... model dator should be a dator!"

        self.model_of = validator_name

        self.my_latest_bet = my_latest_bet
        self.target_estimate = target_estimate

        self.latest_observed_bets = latest_bets

    # model validators use their latest_observed_bets to calculate an estimate
    def my_estimate(self):
        return model_utils.get_estimate_from_latest_messages(self.latest_observed_bets, self.target_estimate)

    # this method makes a bet viewable to the model validator
    def show(self, bet):

        assert isinstance(bet, ModelBet), "...expected a bet!"
        assert bet.estimate == self.target_estimate, "...should only show bets on the target_estimate!"

        self.latest_observed_bets[bet.sender] = bet


    # This function attempts to make a new latest bet for this validator (self) with a given estimate
    def make_new_latest_bet(self):

        if self.my_latest_bet.estimate == self.target_estimate:
            return True, self.my_latest_bet

        if self.my_estimate() == self.target_estimate:
            self.my_latest_bet = ModelBet(self.target_estimate, self.model_of)
            return True, self.my_latest_bet

        return False, None
