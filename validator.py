from settings import VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS
from bet import Bet
from view import View
from safety_oracle import Safety_Oracle
import utils

import random as r
r.seed()

REPORT = False


class Validator:

    # The validator's state is a function of its view and name alone (along with global variables)
    # However, for performance's sake the validator also stores
    @profile
    def __init__(self, name):
        self.name = name
        self.view = View(set())
        self.decided = False

    # The estimator function returns the set of max weight estimates
    # This may not be a single-element set because the validator may have an empty view
    @profile
    def estimator(self):
        return self.view.estimator()

    # The validator checks estimate safety by calling the safety oracle
    # This method also flags the validator as having decided in the case that the estimate is safe
    @profile
    def check_estimate_safety(self, estimate):
        oracle = Safety_Oracle(estimate, self.view)
        is_safe = oracle.check_estimate_safety()
        if is_safe:
            self.decided = True

        return is_safe

    # This function produces a new latest bet for the validator
    # It updates the validator's latest bet, estimate, view, and latest observed bets
    @profile
    def make_new_latest_bet(self):

        # randomly sampling a value returned by the estimator (always returns the single element of a single-element set, btw)
        estimate = r.choice(tuple(self.estimator()))
        justification = self.view.latest_bets
        sender = self.name

        new_latest_bet = Bet(estimate, justification, sender)

        # new_latest_bet.make_redundancy_free()
        self.view.add_bets(set([new_latest_bet]))

        return new_latest_bet

    # This function returns the validator's latest bet
    @profile
    def my_latest_bet(self):
        if self.name in self.view.latest_bets:
            return self.view.latest_bets[self.name]
        else:
            return None

    # This method is the only way that a validator can receive protocol messages
    @profile
    def receive_bets(self, bets):
        if not self.decided:
            self.view.add_bets(bets)
        else:
            print "unable to show bet to decided node"
