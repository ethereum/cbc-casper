# the Bet class implements a DAG of bets...
# ...every bet has a sender, an estimate, and a justification (which is itself
# a set of bets or the empty set)

from settings import VALIDATOR_NAMES, ESTIMATE_SPACE
from justification import Justification
import copy


bet_number = 0


class Bet:
    # we're now going to define the bet constructor (__init__), equality realtion (__eq__), string
    # serialization (__str__), and hash (__hash__)...
    # ...these things are not very conceptually important...

    # constructor!
    @profile
    def __init__(self, estimate, justification, sender):

        # be safe. type check!...
        assert sender in VALIDATOR_NAMES, "...expected a validator!"
        assert estimate in ESTIMATE_SPACE, "...expected an estimate!"
        # assert isinstance(justification, Justification), "expected justification a Justification!"

        # ...then do some assignment
        self.sender = sender
        self.estimate = estimate
        self.justification = copy.copy(justification)

        if self.sender not in self.justification.latest_bets:
            self.sequence_number = 0
        else:
            self.sequence_number = self.justification.latest_bets[self.sender].sequence_number + 1

        if self.justification == dict():
            self.height = 0
        else:
            candidate_max = 0
            for v in self.justification.latest_bets:
                if self.justification.latest_bets[v].height > candidate_max:
                    candidate_max = self.justification.latest_bets[v].height

            self.height = candidate_max + 1

        # ...sorting some things out just for debugging please ignore this!
        global bet_number
        self.id_number = bet_number
        bet_number += 1

    # equality check
    @profile
    def __eq__(self, B):

        # the empty set is not a bet!
        # this saves us from doing if isinstance(b,Bet) and b == set() every time we need to check if we're
        # holding a set() instead of a Bet
        if B is None:
            return False

        # ...but first be safe. type check!
        assert isinstance(B, Bet), "Expected bet as parameter in `=='"

        # two bets are equal only if they have the same estimate, sender and justification...
        # ...it turns out that __eq__ in python's set() uses __eq__ of its members if available, under the hood...
        # ...so this turns out to be a recursive definition! yay, recursion!
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

    # it turns out that to make a set of something in Python, it needs to be hashable!...
    # ...btw it would be cool to show that for two bets A, B with A == B implies str(A) == str(B),..
    # ...which more trivially implies hash(A) == hash(B)...
    # ...so that we don't need to think about counterintuive Python set() behaviour...
    # ...for example if we have set([A]).add(B) = set([A,B]) with hash(A) != hash(B) even though A == B!

    @profile
    def __hash__(self):
        return self.id_number

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

'''
    @profile
    def make_redundancy_free(self):

        dont_check = set()
        for b in self.justification:
            dont_check.add((b, b))

        to_remove_from_justification = set()
        J = list(self.justification)
        for b1 in J:
            for b2 in J:
                if (b1, b2) not in dont_check:
                    if b1.is_dependency(b2):
                        to_remove_from_justification.add(b1)
                        dont_check.add((b2, b1))
        self.justification.difference_update(to_remove_from_justification)
'''
