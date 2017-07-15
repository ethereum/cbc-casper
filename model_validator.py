# The ideal adversary uses the following class to model validators
# The validators will be running a "less safe" version of casper...
# ...one where observing a new latest bet from vi does not (ever, as a rule)
# change the latest bets you've observed from vj != vi

# this class has the folowing attributes:
# model_of
# my_latest_bet
# viewable   #MAYBE QUESTIONABLE DESIGN CHOICE - PERHAPS THE SET OF VIEWABLE BETS FOR A VALIDATOR SHOULD NOT BE A
# PART OF THE VALIDATOR MODEL latest_oberved_bets
from settings import VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS
from bet import Bet
from view import View

import utils


class Model_Validator:
    latest_observed_bets_value_error = """...expected dictionary latest_observed_bets to only contain values
     of a bet or the empty set"""
    my_latest_bet_value_error = """...expected dictionary latest_observed_bets to only contain values
     of a bet or the empty set"""

    @profile
    def __init__(self, validator_name, my_latest_bet, my_latest_observed_bets, viewable, target_estimate):

        # be safe, type check!
        assert target_estimate in ESTIMATE_SPACE, "...expected an estimate!"

        # lets keep a record of the validator that the model is of...
        # this is useful for adding bets from this validator using class functions other than __init__
        assert validator_name in VALIDATOR_NAMES, "expected validator in __init__ of Model_Validator"
        self.model_of = validator_name

        self.my_latest_bet = my_latest_bet
        self.target_estimate = target_estimate

        self.already_committed_view = View(set())

        # These are the bets the validator "can see" from a view given by self.my_latest_bet...
        # ...in the sense that these bets are not already in the extension of its view
        self.viewable = viewable

        # will track the latest bets observed by this model validator
        self.latest_observed_bets = my_latest_observed_bets

    # model validators use their view at my_latest_bet to calculate an estimate, returns set() on failure
    @profile
    def my_estimate(self):

        # otherwise we compute the max score byzantine free estimate
        scores = dict.fromkeys(ESTIMATE_SPACE, 0)

        for v in self.latest_observed_bets:
            assert isinstance(self.latest_observed_bets[v], Bet), """...expected dictionary
              latest_observed_bets to only contain values of a bet or the empty set"""
            scores[self.latest_observed_bets[v].estimate] += WEIGHTS[v]

        max_weight_estimates = utils.get_max_weight_estimates(scores)

        if len(max_weight_estimates) == 1:
            return next(iter(max_weight_estimates))
        else:
            return self.target_estimate

    # this important method makes a bet viewable to the model validator
    # It will only succeed if:
    # * the latest bet from the sender in its dependency
    # * or we haven't heard from the sender before
    @profile
    def make_viewable(self, bet):

        # be safe, type check.
        assert isinstance(bet, Bet), "...expected a bet!"

        if bet.estimate != self.target_estimate or bet.sender in self.viewable:
            return

        # If we haven't observed anything yet, anything is viewable!
        if bet.sender not in self.latest_observed_bets:
            self.viewable[bet.sender] = bet
            return

        assert isinstance(self.latest_observed_bets[bet.sender], Bet), self.latest_observed_bets_value_error

        # We don't need to check if the received bet is after our latest bet observed for bet.sender..
        # ...because this is only called by the adversary in a non-equivocating setting
        self.viewable[bet.sender] = bet

    # This function attempts to make a new latest bet for this validator (self) with a given estimate
    @profile
    def make_new_latest_bet(self):

        if self.my_latest_bet is None:
            new_bet = Bet(self.target_estimate, dict(), self.model_of)
            self.my_latest_bet = new_bet
            return new_bet

        # ...staying safe!
        assert isinstance(self.my_latest_bet, Bet), "...expected my_latest_bet to be a Bet (or the empty set)"
        # empty set would have led to a return above

        # if this validator already has the target estimate as its single latest bet, do nothing... 0,0,1,1
        if self.my_latest_bet.estimate == self.target_estimate:
            return self.my_latest_bet

        # for each validator..
        for v in self.viewable:
            # ...show the viewable (which has the target estimate)
            self.latest_observed_bets[v] = self.viewable[v]

        # if the validators' potential new canonical estimator is target estimate...
        # ...then we'll make a new bet with that estimate and return it...

        if self.my_estimate() == self.target_estimate:

            # make the new bet
            new_latest_bet = Bet(self.target_estimate, self.latest_observed_bets, self.model_of)

            # and update the model parameters accordingly:
            self.my_latest_bet = new_latest_bet

            # finally return
            return True, new_latest_bet

        return False, None
