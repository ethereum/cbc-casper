'''
Casper PoC: Correct-by-construction asynchronous binary consensus.

Note that comments marked with "#########....#########"" barriers are probably
conceptually important Other comments may be conceptually important but are
mostly for code comprehension Note that not all comments have been marked up in
this manner, yet... :)
'''

import sys

import random as r  # to ensure the tie-breaking property

from settings import NUM_VALIDATORS, VALIDATOR_NAMES, WEIGHTS
from bet import Bet
from view import View
from adversary import Adversary
from network import Network



if sys.argv[1:] == ['rounds']:

    network = Network()

    print "WEIGHTS", WEIGHTS

    decided = dict.fromkeys(VALIDATOR_NAMES, 0)
    safe_bets = set()

    network.random_initialization()
    while(True):

        network.report(safe_bets)

        # for i in xrange(NUM_VALIDATORS):
        #    network.validators[i].view.plot_view(safe_bets)

        last_bets = []

        for i in xrange(NUM_VALIDATORS):
            last_bets.append(network.validators[i].my_latest_bet)

        for i in xrange(NUM_VALIDATORS):
            for j in xrange(NUM_VALIDATORS):
                if i != j and (r.randint(0, 4
                    ) == 0):
                    network.propagate_bet_to_validator(last_bets[j], i)

            if not decided[i]:
                new_bet = network.get_bet_from_validator(i)
                decided[i] = network.validators[i].decided

                if decided[i]:
                    safe_bets.add(new_bet)

elif sys.argv[1:] == ['blockchain']:
    
    network = Network()

    print "WEIGHTS", WEIGHTS

    decided = dict.fromkeys(VALIDATOR_NAMES, 0)
    safe_bets = set()

    random_bet = Bet(r.randint(0, 1), set(), 0)
    initial_view = View(set([random_bet]))
    network.view_initialization(initial_view)
    iterator = 0

    while(True):
        network.report(safe_bets)

        #for i in xrange(NUM_VALIDATORS):
        #    network.validators[i].view.plot_view(safe_bets)

        current_validator = iterator % NUM_VALIDATORS
        next_validator = (iterator + 1) % NUM_VALIDATORS

        bet = network.validators[current_validator].my_latest_bet

        if isinstance(bet, Bet):
            network.propagate_bet_to_validator(bet, next_validator)

        if not decided[next_validator]:
            new_bet = network.get_bet_from_validator(next_validator)
            decided[next_validator] = network.validators[next_validator].decided

            if decided[next_validator]:
                safe_bets.add(new_bet)

        iterator += 1
else:
    print "\nusage: 'kernprof -l casper.py rounds' or 'kernprof -l casper.py blockchain'\n"

'''
EXAMPLE 1
'''

WEIGHTS[0] = 3
WEIGHTS[1] = 4
WEIGHTS[2] = 5


for i in xrange(0):
    if i == 0:
        a = Bet(1, [], 0)
        b = Bet(0, [], 1)
        c = Bet(1, [], 2)

        view = View(set([a, b, c]))

        adversary = Adversary(view, 1)
        success, attack_log = adversary.ideal_network_attack()

    if i == 1:
        a = Bet(1, [], 0)
        b = Bet(0, [], 1)
        c = Bet(1, [], 2)
        b2 = Bet(1, [a, b, c], 1)

        view = View(set([a, b, c, b2]))

        adversary = Adversary(view, 1)
        success, attack_log = adversary.ideal_network_attack()

    if i == 2:
        a = Bet(1, [], 0)
        b = Bet(1, [], 1)
        c = Bet(1, [], 2)

        view = View(set([a, b, c]))

        adversary = Adversary(view, 1)
        success, attack_log = adversary.ideal_network_attack()

    if i == 3:

        a = Bet(1, [], 0)
        b = Bet(1, [], 1)
        c = Bet(1, [], 2)

        a1 = Bet(1, [a, b, c], 0)
        b1 = Bet(1, [a, b, c], 1)
        c1 = Bet(1, [a, b, c], 2)

        view = View(set([a, b, c, a1, b1, c1]))

        adversary = Adversary(view, 1)
        success, attack_log = adversary.ideal_network_attack()

    print "-------------------------------Victim View--------------------------------------------"
    print str(view)

    if success:
        print "Ideal network was attack successful..."
    else:
        print "Ideal network was attack unsuccessful..."

    if success:
        print "...with the following operations_log:"
        for l in attack_log:
            print l

        print "-------------------------------Post-attack View-----------------------------------"
        print str(adversary.attack_view)

    view.plot_view()
    adversary.attack_view.plot_view()
