'''
Casper PoC: Correct-by-construction asynchronous binary consensus.

Note that comments marked with "#########....#########"" barriers are probably
conceptually important Other comments may be conceptually important but are
mostly for code comprehension Note that not all comments have been marked up in
this manner, yet... :)
'''

import sys

import random as r  # to ensure the tie-breaking property

from settings import NUM_VALIDATORS, VALIDATOR_NAMES, WEIGHTS, REPORT_INTERVAL, NUM_MESSAGES_PER_ROUND, REPORT_SUBJECTIVE_VIEWS
from bet import Bet
from view import View
from adversary import Adversary
from network import Network


@profile
def main():
    if sys.argv[1] == 'rounds':

        network = Network()

        print "WEIGHTS", WEIGHTS

        decided = dict.fromkeys(VALIDATOR_NAMES, 0)
        safe_bets = set()

        network.random_initialization()

        edges = []
        iterator = 0
        while(True):

            if iterator % REPORT_INTERVAL == 0:
                network.report(safe_bets,edges)
                if REPORT_SUBJECTIVE_VIEWS:
                    for i in xrange(NUM_VALIDATORS):
                        network.validators[i].view.plot_view(safe_bets, use_edges=edges)

            iterator += 1

            pairs = []
            for i in xrange(NUM_VALIDATORS):
                for j in xrange(NUM_VALIDATORS):
                    if i != j:
                        pairs.append([i, j])

            messages = []

            for i in xrange(NUM_MESSAGES_PER_ROUND):
                message_path = r.sample(pairs, 1)
                messages.append(message_path[0])
                pairs.remove(message_path[0])

            last_bets = []
            validator_received_bet = set()
            for i in xrange(NUM_VALIDATORS):
                last_bets.append(network.validators[i].my_latest_bet)

            for sb in list(safe_bets):
                if sb not in last_bets:
                    raise Exception("safe bets should be in last bets")  # sanity check

            for path in messages:
                i = path[0]
                j = path[1]
                network.propagate_bet_to_validator(last_bets[i], j)
                validator_received_bet.add(j)

            for i in xrange(NUM_VALIDATORS):
                if not decided[i] and i in validator_received_bet:
                    new_bet = network.get_bet_from_validator(i)
                    decided[i] = network.validators[i].decide_if_safe(new_bet.estimate)

                    if decided[i]:
                        safe_bets.add(new_bet)

            for path in messages:
                edges.append([last_bets[path[0]], network.validators[path[1]].my_latest_bet])
                edges.append([last_bets[path[1]], network.validators[path[1]].my_latest_bet])

    elif sys.argv[1] == 'blockchain':

        network = Network()

        print "WEIGHTS", WEIGHTS

        decided = dict.fromkeys(VALIDATOR_NAMES, 0)
        safe_bets = set()

        random_bet = Bet(r.randint(0, 1), dict(), 0)
        initial_view = View(set([random_bet]))
        network.view_initialization(initial_view)
        iterator = 0
        edges = []

        while(True):

            if iterator % REPORT_INTERVAL == 0:
                network.report(safe_bets, edges)
                if REPORT_SUBJECTIVE_VIEWS:
                    for i in xrange(NUM_VALIDATORS):
                        network.validators[i].view.plot_view(safe_bets, use_edges=edges)

            # for i in xrange(NUM_VALIDATORS):
            #    network.validators[i].view.plot_view(safe_bets)

            current_validator = iterator % NUM_VALIDATORS
            next_validator = (iterator + 1) % NUM_VALIDATORS

            bet = network.validators[current_validator].my_latest_bet

            if isinstance(bet, Bet):
                network.propagate_bet_to_validator(bet, next_validator)

            if not decided[next_validator]:
                new_bet = network.get_bet_from_validator(next_validator)
                decided[next_validator] = network.validators[next_validator].decide_if_safe(new_bet.estimate)

                edges.append([bet, new_bet])

                if decided[next_validator]:
                    safe_bets.add(new_bet)

            iterator += 1
    else:
        print "\nusage: 'kernprof -l casper.py rounds' or 'kernprof -l casper.py blockchain'\n"

main()
