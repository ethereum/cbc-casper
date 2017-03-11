import random as r  # to ensure the tie-breaking property
import sys
import json

from settings import VALIDATOR_NAMES
from view import View
from validator import Validator


class Network:
    def __init__(self):
        self.validators = dict()
        for v in VALIDATOR_NAMES:
            self.validators[v] = Validator(v)
        self.global_view = set()

        # Plot view data used for our visualizations
        self.plot_view_data = []

    def propagate_bet_to_validator(self, bet, validator_name):
        assert bet in self.global_view, "...expected only to propagate bets from the global view"
        self.validators[validator_name].show_single_bet(bet)

    def get_bet_from_validator(self, validator_name):
        assert validator_name in VALIDATOR_NAMES, "...expected a known validator"

        if self.validators[validator_name].decided:
            return True

        new_bet = self.validators[validator_name].make_new_latest_bet()
        self.global_view.add(new_bet)

    def random_propagation_and_bet(self):

        destination = r.choice(tuple(VALIDATOR_NAMES))
        if len(self.global_view) == 0:
            self.get_bet_from_validator(destination)
        else:
            bet = r.choice(tuple(self.global_view))
            self.propagate_bet_to_validator(bet, destination)
            self.get_bet_from_validator(destination)

    def random_initialization(self):
        for v in VALIDATOR_NAMES:
            self.get_bet_from_validator(v)

        if __debug__:
            print str(self.global_view)

    def report(self, decided):
        self.plot_view_data.append(View(self.global_view).plot_view(decided))

        is_all_decided = True
        for sender, is_decided in decided.iteritems():
            if not is_decided:
                is_all_decided = False

        if not is_all_decided:
            return

        # We already decided on all nodes, so let's return the data and call it a day!
        print(json.dumps(self.plot_view_data))
        sys.exit(0)
