# the Bet class implements a DAG of bets...
# ...every bet has a sender, an estimate, and a justification (which is itself
# a set of bets or the empty set)

from settings import VALIDATOR_NAMES, ESTIMATE_SPACE

bet_number = 0


class Bet:
    # we're now going to define the bet constructor (__init__), equality realtion (__eq__), string
    # serialization (__str__), and hash (__hash__)...
    # ...these things are not very conceptually important...

    # constructor!
    def __init__(self, estimate, justification, sender):

        # be safe. type check!...
        assert sender in VALIDATOR_NAMES, "...expected a validator!"
        assert estimate in ESTIMATE_SPACE, "...expected an estimate!"
        for b in justification:  # anything iterable, containing bets
            assert isinstance(b, Bet), "...expected there to be only bets in the justification!"

        # ...then do some assignment
        self.sender = sender
        self.estimate = estimate
        self.justification = set()
        for b in justification:
            self.justification.add(b)

        # ...sorting some things out just for debugging please ignore this!
        global bet_number
        self.id_number = bet_number
        bet_number += 1

    # equality check
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
    def __str__(self):
        string = "("
        string += str(self.estimate) + ", {"
        i = 0
        # if this following line of code sometimes produces different orders (justification is a set), then
        # we have an issue. It would be good practice to give a standard for ordering bets in justifications.
        for b in self.justification:
            string += str(b)
            i += 1
            if i != len(self.justification):  # getting fancy; leaving out commas without successive terms
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

    #####################################################################################
    # a bet A is a dependency of a bet B if either...
    # ...A is in the justification of B...
    # ...or A is in the dependency of bets in the justification of B!
    #####################################################################################

    # this function checks if this bet (self) is a dependency of some bet B...

    @profile
    def recursive_is_dependency(self, B, is_checked):

        # be safe, type check!
        # self is definitely a dependency of B if it is in the justification...
        if self in B.justification:
            return True

        is_checked[B] = True

        # ...or if it is in the dependency of anything in the justification!
        for b in B.justification:
            if b not in is_checked:
                if self.recursive_is_dependency(b, is_checked):
                    return True

        # if neither of these, then "self" is not a dependency of B!
        return False

    @profile
    def is_dependency(self, B):

        assert isinstance(B, Bet), "...expected a bet!"

        is_checked = dict()

        return self.recursive_is_dependency(B, is_checked)

    # this one gets all the bets in the dependency of this bet (self)...
    # ...it puts them into a set, and returns that!
    @profile
    def dependency(self):
        dependencies = set()

        # recurr into the justification to find all dependencies and add them to our set "d"
        def recurr(B):
            for b in B.justification:  # recursion bottoms on empty iterable
                dependencies.add(b)  # note that .add in set() checks if __hash__ does not already appear!
                recurr(b)

        # now we're calling it:
        recurr(self)

        # we did it!
        return dependencies

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
