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

    def __init__(self, model_of_validator, view):

        # lets keep a record of the validator that the model is of...
        # this is useful for adding bets from this validator using class functions other than __init__
        assert model_of_validator in VALIDATOR_NAMES, "expected validator in __init__ of Model_Validator"
        self.model_of = model_of_validator

        # for good measure, lets make sure that we really have a view, here...
        assert isinstance(view, View), "expected view in __init__ of Model_Validator"

        self.my_latest_bet = view.LatestBets()[self.model_of]

        self.already_committed_view = View(set())

        # These are the bets the validator "can see" from a view given by self.my_latest_bet...
        # ...in the sense that these bets are not already in the extension of its view
        self.viewable = dict()
        for v in VALIDATOR_NAMES:
            self.viewable[v] = set()

        # will track the latest bets observed by this model validator
        self.latest_observed_bets = dict()

        # if this validator has no latest bets in the view, then we store...
        if self.my_latest_bet is None:

            # ...an empty dictionary of latest observed bets...
            for v in VALIDATOR_NAMES:
                self.latest_observed_bets[v] = None

            # for validators without anything in their view, any bets are later bets are viewable bets!
            # ...so we add them all in!
            for b in view.Extension():
                self.viewable[b.sender].add(b)

        # if we do have a latest bet from this validator, then...
        else:
            assert isinstance(self.my_latest_bet, Bet), "...expected my_latest_bet to be a bet or the empty set"

            # we can get the latest bets in our standard way
            my_view = View(set([self.my_latest_bet]))
            self.latest_observed_bets = my_view.LatestBets()

            # then all bets that are causally after these bets are viewable by this validator
            for b in view.Extension():
                # ...we use the is_dependency relation to test if b is causally after the
                # latest bet observed from that sender
                if self.latest_observed_bets[b.sender] is None:
                    self.viewable[b.sender].add(b)
                else:
                    assert isinstance(self.latest_observed_bets[b.sender], Bet), """...expected dictionary
                     latest_observed_bets to only contain values of a bet or the empty set"""

                    # if b is later than the latest observed bet from b.sender,
                    # then b is viewable to this model validator
                    if self.latest_observed_bets[b.sender].is_dependency(b):
                        self.viewable[b.sender].add(b)

    # model validators use their view at my_latest_bet to calculate an estimate, returns set() on failure
    def my_estimate(self):

        # otherwise we compute the max score byzantine free estimate
        scores = dict.fromkeys(ESTIMATE_SPACE, 0)

        for v in VALIDATOR_NAMES:
            if self.latest_observed_bets[v] is None:
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
            raise Exception("...expected a non-empty view")

    # this important method makes a bet viewable to the model validator
    # It will only succeed if:
    # * the latest bet from the sender in its dependency
    # * or we haven't heard from the sender before
    def make_viewable(self, bet):

        # be safe, type check.
        assert isinstance(bet, Bet), "...expected a bet!"

        # If we haven't observed anything yet, anything is viewable!
        if self.latest_observed_bets[bet.sender] is None:
            self.viewable[bet.sender].add(bet)
            return True
        else:
            assert isinstance(self.latest_observed_bets[bet.sender], Bet), self.latest_observed_bets_value_error
            # This is the "normal case", where a bet from a validator is viewable only if
            # the latest bet is in its dependency
            if self.latest_observed_bets[bet.sender].is_dependency(bet):
                self.viewable[bet.sender].add(bet)
                return True
            else:
                return False

    # this method goes through the viewables and removes any bets that are a dependency latest bets from the same sender
    # this function should be run every time a model validator is shown a new latest_bet
    @profile
    def update_viewable(self):

        # ...looping over the validators
        for v in VALIDATOR_NAMES:

            # ...if we do have a latest bet from them...
            if self.latest_observed_bets[v] is None:
                continue
            else:
                assert isinstance(self.latest_observed_bets[v], Bet), self.latest_observed_bets_value_error

                # then we can remove all bets in viewable which are dependencies of this latest bet...
                # ...but we can't remove them during the iteration, so we store the bets to be removed in this set...
                to_remove_from_viewable = set()

                for b in self.viewable[v]:
                    if b.is_dependency(self.latest_observed_bets[v]):
                        to_remove_from_viewable.add(b)

                # finally, updating the viewable for this validator
                self.viewable[v] = self.viewable[v].difference(to_remove_from_viewable)

    # This function attempts to make a new latest bet for this validator (self) with a given estimate
    @profile
    def make_new_latest_bet_with_estimate(self, target_estimate):

        # be safe, type check!
        assert target_estimate in ESTIMATE_SPACE, "...expected an estimate!"

        if self.my_latest_bet is None:
            new_bet = Bet(target_estimate, [], self.model_of)
            self.my_latest_bet = new_bet
            return new_bet

        # ...staying safe!
        assert isinstance(self.my_latest_bet, Bet), "...expected my_latest_bet to be a Bet (or the empty set)"
        # empty set would have led to a return above

        # if this validator already has the target estimate as its single latest bet, do nothing... 0,0,1,1
        if self.my_latest_bet.estimate == target_estimate:
            return self.my_latest_bet

        # for each validator..
        for v in VALIDATOR_NAMES:

            if self.latest_observed_bets[v] is None or self.latest_observed_bets[v].estimate != target_estimate:

                # and if their latest estimate is not the target estimate...

                # ... in the set of their bets "viewable" to this validator...
                # (note our reliance on the viewable set to make latest bets)
                for b in self.viewable[v]:
                    # ...and if we find one with the target estimate
                    if b.estimate == target_estimate:
                        self.latest_observed_bets[v] = b
                        break

        # recall that we need to update the viewable set after making any changes to the latest bets!
        self.update_viewable()

        # if the validators' potential new canonical estimator is target estimate...
        # ...then we'll make a new bet with that estimate and return it...
        # ...otherwise we throw an exception

        try:

            if self.my_estimate() == target_estimate:

                justification = set()
                for v in VALIDATOR_NAMES:
                    if self.latest_observed_bets[v] is not None:
                        justification.add(self.latest_observed_bets[v])

                to_be_removed = set()
                for j in justification:
                    if j in self.already_committed_view.bets:
                        to_be_removed.add(j)
                justification.difference_update(to_be_removed)

                self.already_committed_view.add_view(View(justification))

                # make the new bet
                new_latest_bet = Bet(target_estimate, justification, self.model_of)

                # and update the model parameters accordingly:
                self.my_latest_bet = new_latest_bet

                # finally return
                return new_latest_bet
            else:
                raise Exception("Unable to make legal bet with the target estimate at the given position")
        except:
            raise Exception("...expected a non-empty view")
