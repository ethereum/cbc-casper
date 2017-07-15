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
        self.my_latest_bet = None
        self.my_latest_estimate = None
        self.latest_observed_bets = dict()  # This stores the latest bets seen by the validator
        self.vicarious_latest_bets = dict()  # This stores the latest bets committed to have been seen by other validaotrs in their latest bets
        for v in VALIDATOR_NAMES:
            self.vicarious_latest_bets[v] = dict()

    # The estimator function returns the set of max weight estimates
    # This may not be a single-element set because the validator may have an empty view
    @profile
    def estimator(self):
        scores = dict.fromkeys(ESTIMATE_SPACE, 0)
        for v in VALIDATOR_NAMES:
            if v in self.latest_observed_bets:
                scores[self.latest_observed_bets[v].estimate] += WEIGHTS[v]

        return utils.get_max_weight_estimates(scores)

    # The validator checks estimate safety by calling the safety oracle
    # This method also flags the validator as having decided in the case that the estimate is safe
    @profile
    def check_estimate_safety(self, estimate):
        oracle = Safety_Oracle(estimate, self.latest_observed_bets, self.vicarious_latest_bets)
        safe = oracle.check_estimate_safety()
        if safe:
            self.decided = True

        return safe

    # This function produces a new latest bet for the validator
    # It updates the validator's latest bet, estimate, view, and latest observed bets
    @profile
    def make_new_latest_bet(self):

        estimates = self.estimator()

        if len(estimates) == 1:
            estimate = next(iter(estimates))
        else:
            estimate = r.choice(tuple(estimates))

        justification = self.latest_observed_bets
        sender = self.name

        self.my_latest_bet = Bet(estimate, justification, sender)
        # self.my_latest_bet.make_redundancy_free()
        self.my_latest_estimate = estimate
        self.view.add_bet(self.my_latest_bet)
        self.latest_observed_bets[self.name] = self.my_latest_bet

        return self.my_latest_bet

    # This method updates a validators latest bets (and vicarious latest bets) in response to seeing new bets
    @profile
    def update_latest_bets(self, showed_bets):

        '''
        PART 1 - updating latest bets
        '''

        sequence_numbers = dict()
        for v in self.latest_observed_bets:
            sequence_numbers[v] = self.latest_observed_bets[v].sequence_number

        newly_discovered_bets = View(showed_bets).get_extension_up_to_sequence_numbers(sequence_numbers)

        # updating latest bets..
        for b in newly_discovered_bets:

            if b.sender not in self.latest_observed_bets:
                self.latest_observed_bets[b.sender] = b
                continue

            if self.latest_observed_bets[b.sender].sequence_number < b.sequence_number:
                self.latest_observed_bets[b.sender] = b
                continue

            assert (b == self.latest_observed_bets[b.sender] or
                    b.is_dependency_from_same_validator(self.latest_observed_bets[b.sender])), "...did not expect any equivocating nodes!"

        '''
        PART 2 - updating vicarious latest bets
        '''

        # updating vicarious_latest_bets for validator v, for all v..
        for v in self.latest_observed_bets:
            self.vicarious_latest_bets[v] = self.latest_observed_bets[v].justification

    # This method is the only way that a validator can receive protocol messages
    @profile
    def receive_bets(self, bets):
        if not self.decided:
            for bet in bets:
                self.view.add_bet(bet)
            self.update_latest_bets(bets)
        else:
            print "unable to show bet to decided node"
