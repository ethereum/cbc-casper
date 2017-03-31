# the Adversary class has the properties:
# victim_estimate
# target_estimate
# attack_view
# validator_models
# attack_surface
# voting_with_attacker
# voting_against_attacker
# not_voted_yet
# latest_bets
# weight_of_victim_estimate
# weight_of_target_estimate
# attack_delta
# operation_log
import copy   # hopefully this does not end up being used

from settings import VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS
from bet import Bet
from view import View
from model_validator import Model_Validator


class Adversary:

    @profile
    def __init__(self, view, victim_estimate, latest_observed_bets, vicarious_latest_bets, viewables):

        # be safe! start with type checking.
        assert isinstance(view, View), "...expected a View!"
        assert victim_estimate in ESTIMATE_SPACE, "...expected an estimate!"

        # The adversary has particular estimate that she wants to attack (the victim estimate)...
        self.victim_estimate = victim_estimate

        # ...and a particular estimate she wants to cause to win (the target estimate)...
        self.target_estimate = 1 - victim_estimate  # this will need to change when we go from binary to n-ary

        # the attacker keeps a copy of the parameter view, to which she will add attacking bets...
        self.attack_view = copy.deepcopy(view)

        # ...and she will keep track of the latest estimates from these validators, if unique
        self.latest_bets = latest_observed_bets
        self.vicarious_latest_bets = vicarious_latest_bets

        # ...and she also keeps models of every validator!
        self.validator_models = dict()
        for v in VALIDATOR_NAMES:
            if v in self.latest_bets:
                self.validator_models[v] = Model_Validator(v, self.latest_bets[v], self.vicarious_latest_bets[v], viewables[v], self.target_estimate)
            else:
                self.validator_models[v] = Model_Validator(v, None, self.vicarious_latest_bets[v], viewables[v], self.target_estimate)

        # she's going to use this dictionary to keep track of the attack surface
        self.attack_surface = dict()
        for v in VALIDATOR_NAMES:
            self.attack_surface[v] = dict.fromkeys(VALIDATOR_NAMES, True)

        # our adversary is going to classify non-Byzantine validators into the following categories...
        self.voting_with_attacker = set()
        self.voting_against_attacker = set()
        self.not_voted_yet = set()

        for v in VALIDATOR_NAMES:
            if v not in self.latest_bets:
                self.not_voted_yet.add(v)
            else:
                assert isinstance(self.latest_bets[v], Bet), "...expected latest_bets to have None or a Bet"
                if self.latest_bets[v].estimate == self.victim_estimate:
                    # if v's latest estimate is the victim estimate...
                    self.voting_against_attacker.add(v)  # ... then v is "voting against" the attacker
                elif self.latest_bets[v].estimate == self.target_estimate:
                    # if v's latest estimate is the target estimate...
                    self.voting_with_attacker.add(v)  # ...great! v is helping the attacker!

        # if you're voting with the attacker...
        # ...she'll take you out of the attack surface!
        for v in self.voting_with_attacker:
            self.attack_surface.pop(v)

        # The attacker will also keep a close eye on the weights of the victim and target estimates:
        self.weight_of_victim_estimate = 0
        for v in self.voting_against_attacker:
            self.weight_of_victim_estimate += WEIGHTS[v]

        self.weight_of_target_estimate = 0
        for v in self.voting_with_attacker:
            self.weight_of_target_estimate += WEIGHTS[v]

        # the "attack delta" is "the advantage" of the victim estimate over the target estimate
        self.attack_delta = self.weight_of_victim_estimate - self.weight_of_target_estimate

        # the attacker produces a log of the bets added during the attack...
        self.operations_log = []

    # this method updates the attack delta using the Adversary's record of the victim and target estimate weights...
    def update_attack_delta(self):
        self.attack_delta = self.weight_of_victim_estimate - self.weight_of_target_estimate

    # ...and this one returns "True" if the attack delta is less than or equal to zero
    # (indicating target weight >= victim weight)...
    # ...and it returns "False" otherwise...
    def is_attack_complete(self):
        if self.attack_delta <= 0:
            return True
        else:
            return False

    # this method implements an ideal network attack...
    # ...it returns the pair (True, self.operation_log) if the attack is successful
    # ...and (False, self.operatrion_log) otherwise
    @profile
    def ideal_network_attack(self):

        # We'll continue the attack until we no longer make progress
        # Or until the attack is successful and the victim estimate dethroned
        progress_made = True
        while progress_made:
            progress_made = False

            # the "network-only" attack has two phases...
            #  1) adding bets (with the target estimate) from unobserved validators
            #  2) adding new latest bets (with the target estimate) from validators currently voting against the
            #     attacker

            ######
            # Phase 1: observing unobserved validators
            ######

            # the for loop here well de-facto only be executed once...
            # ...because not_voted_yet == set() after ths first complete iteration!
            for v in self.not_voted_yet:

                # these ones are easy...!
                new_bet = self.validator_models[v].make_new_latest_bet()
                # btw: never returns an exception

                # ...becuase progress here is guaranteed!
                progress_made = True

                # so lets make a log of our operations...
                self.operations_log.append(["bet added from previously-unobserve validator", str(new_bet)])

                # ...update validator status...
                # ...remove v from "has_not_voted" and add to "voting_with_attacker"...
                self.voting_with_attacker.add(v)

                # ...remove v from the attack surface...
                self.attack_surface.pop(v)

                # ...update weights + attack delta...
                self.weight_of_target_estimate += WEIGHTS[v]

                # ...add new bet to the latest_bets vector...
                self.latest_bets[v] = new_bet

                # ...make this bet viewable to all those still voting against the attacker
                for v2 in self.voting_against_attacker:
                    self.validator_models[v2].make_viewable(new_bet)

                # ...update the attack view...
                self.attack_view.add_bet(new_bet)

                # ...and update the attack delta!
                self.update_attack_delta()

                # if we can end the attack, then lets return our success
                if self.is_attack_complete():
                    return True, self.operations_log

            # updating the set of validators who haven't voted yet...
            # ...to the empty set, because after this loop all validators have voted.
            self.not_voted_yet = set()

            ######
            # Phase 2: "voting against" validators
            ######

            # we cannot change the size of the interable while iterating over it...
            # ...so we're going to collect the validators we want to remove from "voting against", here...
            # ...and remove them all at once, when we reach the end of the for loop!
            to_remove_from_voting_against_attacker = set()

            # For each validator who is voting against the attacker..
            for v in self.voting_against_attacker:

                # lets have a quick precautionary sanity check...!
                assert isinstance(self.latest_bets[v], Bet), """...expected validators voting_against_attacker to have
                     exactly one latest bet"""

                # ...try to add a new bet from this validator with the estimate of the attacker's choosing

                success, new_bet = self.validator_models[v].make_new_latest_bet()

                # If we failed to add a bet with the estimate of the attacker's choosing for this validator..
                # ..continue to the next one so we can keep trying
                if not success:
                    continue

                # If new bet successful...

                # ...record that progress was made
                progress_made = True

                # ...remove the sender from the attack surface...
                self.attack_surface.pop(v)

                # ...we would like to move the validator from "voting against" to "voting with"...
                to_remove_from_voting_against_attacker.add(v)
                # ...but actually we can only mark them for later removal because we are currently
                # iterating over "voting_against"
                self.voting_with_attacker.add(v)  # ...however we can add them to "voting_with"

                # ...record that we made 2X "weights[v]" of progress...
                self.weight_of_victim_estimate -= WEIGHTS[v]
                self.weight_of_target_estimate += WEIGHTS[v]
                self.update_attack_delta()

                # ...update our latest bets...
                self.latest_bets[v] = new_bet

                # ...make this bet "viewable" to all validators who are still voting against the attacker...
                for v2 in self.voting_against_attacker.difference(to_remove_from_voting_against_attacker):
                    self.validator_models[v2].make_viewable(new_bet)

                # ...updating the attack view
                self.attack_view.add_bet(new_bet)

                # ...add a log of our operations
                self.operations_log.append(["added valid bet for a validator voting against the attacker",
                                            hash(new_bet)])

                if self.is_attack_complete():
                    return True, self.operations_log

            # now that the attack loop is done, we can remove the
            # validators who made new bets from the "voting_against" set
            self.voting_against_attacker.difference_update(to_remove_from_voting_against_attacker)

            # if the attack was complete, it should have been captured at
            # the end of the for loops for phases 1 or 2 of the network attack!
            assert not self.is_attack_complete(), "...expected attack to be ongoing, at this point"

        # if ever we exist the while(progress_made) loop with progress_made == False
        # rather than a return value, then the attack has failed
        assert not progress_made, "...expected to exit loop only when progress is not made"
        return False, self.operations_log
