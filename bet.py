# the Bet class implements a DAG of bets...
# ...every bet has a sender, an estimate, and a justification (which is itself
# a set of bets or the empty set)

from settings import VALIDATOR_NAMES, ESTIMATE_SPACE
from justification import Justification
import copy


class Bet:
    @profile
    def __init__(self, estimate, justification, sender):

        # be safe. type check!...
        assert sender in VALIDATOR_NAMES, "...expected a validator!"
        assert estimate in ESTIMATE_SPACE, "...expected an estimate!"
        assert isinstance(justification, Justification), "expected justification a Justification!"

        # these are the key elements of a bet
        self.sender = sender
        self.estimate = estimate
        self.justification = copy.copy(justification)

        # the sequence number makes certain operations more efficient (like checking if bets are later)
        if self.sender not in self.justification.latest_bets:
            self.sequence_number = 0
        else:
            self.sequence_number = self.justification.latest_bets[self.sender].sequence_number + 1

        # the "heights" of bets are used for visualization of views
        if self.justification.is_null():
            self.height = 0
        else:
            candidate_max = 0
            for v in self.justification.latest_bets:
                if self.justification.latest_bets[v].height > candidate_max:
                    candidate_max = self.justification.latest_bets[v].height

            self.height = candidate_max + 1

    @profile
    def __eq__(self, B):
        if B is None:
            return False

        assert isinstance(B, Bet), "Expected bet as parameter in `=='"

        if self.estimate != B.estimate \
            or self.sender != B.sender \
                or B.justification != self.justification:
            return False
        return True

    # this is not an efficient serialization, because bets are included redundantly
    # but this does serialize bets nicely, like this: "(1, {(1, {}, 0)}, 1)"...!
    @profile
    def __str__(self):
        string = "("
        string += str(self.estimate) + ", {"
        i = 0
        # if this following line of code sometimes produces different orders (justification is a set), then
        # we have an issue. It would be good practice to give a standard for ordering bets in justifications.
        for b in self.justification.latest_bets.values():
            string += str(b)
            i += 1
            if i != len(self.justification.latest_bets):  # getting fancy; leaving out commas without successive terms
                string += ", "
        string += "}, " + str(self.sender) + ")"
        return string

    @profile
    def __hash__(self):
        return self.id_number

    # this method can be used to check if a bet is valid
    def is_valid(self):
        return self.estimate == self.justification.estimate()

    @profile
    def recursive_is_dependency_from_same_validator(self, B):

        # this is the case where we get to the sender's first Bet before finding this bet
        if self.sender not in B.justification.latest_bets:
            return False

        if self == B.justification.latest_bets[self.sender]:
            return True

        return self.recursive_is_dependency_from_same_validator(B.justification.latest_bets[self.sender])

    @profile
    def is_dependency_from_same_validator(self, B):
        assert isinstance(B, Bet), "...expected a bet!"
        assert B.sender == self.sender, "...expected bets to be from the same validator"

        return self.recursive_is_dependency_from_same_validator(B)
