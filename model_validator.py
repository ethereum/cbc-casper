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


class Model_Validator:
    latest_observed_bets_value_error = """...expected dictionary latest_observed_bets to only contain values
     of a bet or the empty set"""
    my_latest_bet_value_error = """...expected dictionary latest_observed_bets to only contain values
     of a bet or the empty set"""

    @profile
    def __init__(self, model_of_validator, view, my_latest_bet, my_latest_observed_bets, target_estimate):

        # be safe, type check!
        assert target_estimate in ESTIMATE_SPACE, "...expected an estimate!"

        # lets keep a record of the validator that the model is of...
        # this is useful for adding bets from this validator using class functions other than __init__
        assert model_of_validator in VALIDATOR_NAMES, "expected validator in __init__ of Model_Validator"
        self.model_of = model_of_validator

        # for good measure, lets make sure that we really have a view, here...
        assert isinstance(view, View), "expected view in __init__ of Model_Validator"

        self.my_latest_bet = my_latest_bet
        self.target_estimate = target_estimate

        self.already_committed_view = View(set())

        # These are the bets the validator "can see" from a view given by self.my_latest_bet...
        # ...in the sense that these bets are not already in the extension of its view
        self.viewable = dict()

        # will track the latest bets observed by this model validator
        self.latest_observed_bets = my_latest_observed_bets

        # if this validator has no latest bets in the view, then we store...
        if self.my_latest_bet is None:

            # for validators without anything in their view, any bets are later bets are viewable bets!
            # ...so we add them all in!
            for b in view.get_extension():
                if b.estimate == self.target_estimate and b.sender not in self.viewable:
                    self.viewable[b.sender] = b

        # if we do have a latest bet from this validator, then...
        else:
            assert isinstance(self.my_latest_bet, Bet), "...expected my_latest_bet to be a bet or the empty set"

            # we can get the latest bets in our standard way
            my_view = View(set([self.my_latest_bet]))

            # then all bets that are causally after these bets are viewable by this validator
            for b in view.get_extension():

                if b.sender in self.viewable:
                    continue

                if b.estimate != self.target_estimate:
                    continue

                # ...we use the is_dependency relation to test if b is causally after the
                # latest bet observed from that sender
                if b.sender not in self.latest_observed_bets:
                    self.viewable[b.sender] = b
                else:
                    assert isinstance(self.latest_observed_bets[b.sender], Bet), """...expected dictionary
                     latest_observed_bets to only contain values of a bet or the empty set"""

                    # if b is later than the latest observed bet from b.sender,
                    # then b is viewable to this model validator
                    if self.latest_observed_bets[b.sender].is_dependency(b):
                        self.viewable[b.sender] = b

    # model validators use their view at my_latest_bet to calculate an estimate, returns set() on failure
    @profile
    def my_estimate(self):

        # otherwise we compute the max score byzantine free estimate
        scores = dict.fromkeys(ESTIMATE_SPACE, 0)

        for v in VALIDATOR_NAMES:
            if v not in self.latest_observed_bets:
                continue
            else:
                assert isinstance(self.latest_observed_bets[v], Bet), """...expected dictionary
                  latest_observed_bets to only contain values of a bet or the empty set"""
                scores[self.latest_observed_bets[v].estimate] += WEIGHTS[v]

        # get the max score
        max_score = 0
        for e in ESTIMATE_SPACE:
            if scores[e] > max_score:
                max_score = scores[e]
                max_score_estimate = e

            # check that we have a max_score greater than zero:
        # note that here we are requiring the tie-breaking property.
        if max_score > 0:
            return max_score_estimate
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
            new_bet = Bet(self.target_estimate, [], self.model_of)
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
            justification = set()
            for v in VALIDATOR_NAMES:
                if v in self.latest_observed_bets:
                    justification.add(self.latest_observed_bets[v])

            to_be_removed = set()
            for j in justification:
                if j in self.already_committed_view.bets:
                    to_be_removed.add(j)
            justification.difference_update(to_be_removed)

            self.already_committed_view.add_view(View(justification))

            # make the new bet
            new_latest_bet = Bet(self.target_estimate, justification, self.model_of)

            # and update the model parameters accordingly:
            self.my_latest_bet = new_latest_bet

            # finally return
            return True, new_latest_bet

        return False, None
