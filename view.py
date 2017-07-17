import utils
from bet import Bet
from settings import NUM_VALIDATORS, VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS
import plot_tool


class View:
    @profile
    def __init__(self, bets):
        # be safe, type check!
        for b in bets:
            assert isinstance(b, Bet), "...expected only bets in view"

        # now for some assignment...
        self.bets = set()
        self.latest_bets = dict()

        self.add_bets(bets)

    @profile
    def __str__(self):
        s = "View: \n"
        for b in self.bets:
            s += str(b) + "\n"
        return s

    # The estimator function returns the set of max weight estimates
    # This may not be a single-element set because the validator may have an empty view
    @profile
    def estimator(self):
        return utils.get_estimate_from_justification(self.latest_bets)

    # This method updates a validator's observed latest bets (and vicarious latest bets) in response to seeing new bets
    @profile
    def add_bets(self, showed_bets):

        '''
        PART -1 - type check
        '''

        for b in showed_bets:
            assert isinstance(b, Bet), "expected only to add bets"

        '''
        PART 0 - finding newly discovered bets
        '''

        newly_discovered_bets = self.get_new_bets(showed_bets)

        '''
        PART 1 - updating the set of viewed bets
        '''

        for b in newly_discovered_bets:
            self.bets.add(b)

        '''
        PART 2 - updating latest bets
        '''

        # updating latest bets..
        for b in newly_discovered_bets:
            if b.sender not in self.latest_bets:
                self.latest_bets[b.sender] = b
                continue
            if self.latest_bets[b.sender].sequence_number < b.sequence_number:
                self.latest_bets[b.sender] = b
                continue
            assert (b == self.latest_bets[b.sender] or
                    b.is_dependency_from_same_validator(self.latest_bets[b.sender])), "...did not expect any equivocating nodes!"

    # This method returns the set of bets out of showed_bets and their dependency that isn't part of the view
    @profile
    def get_new_bets(self, showed_bets):

        new_bets = set()
        # The memo will keep track of bets we've already looked at, so we don't redo work.
        memo = set()

        # At the start, our working set will be the "showed bets" parameter
        current_set = set(showed_bets)
        while(current_set != set()):

            next_set = set()
            # If there's no bet in the current working set
            for bet in current_set:

                # Which we haven't seen it in the view or during this loop
                if bet not in self.bets and bet not in memo:

                    # But if we do have a new bet, then we add it to our pile..
                    new_bets.add(bet)

                    # and add the best in its justification to our next working set
                    for b in bet.justification.latest_bets.values():
                        next_set.add(b)
                # Keeping a record of very bet we inspect, being sure not to do any extra (exponential complexity) work
                memo.add(bet)

            current_set = next_set

        # After the loop is done, we return a set of new bets
        return new_bets

    @profile
    def plot_view(self, coloured_bets, colour='green', use_edges=[]):
        plot_tool.plot_view(self, coloured_bets, colour, use_edges)
