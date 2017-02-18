'''
Casper PoC: Correct-by-construction asynchronous binary consensus.

Note that comments marked with "#########....#########"" barriers are probably
conceptually important Other comments may be conceptually important but are
mostly for code comprehension Note that not all comments have been marked up in
this manner, yet... :)
'''
import random as r  # to ensure the tie-breaking property

from settings import NUM_VALIDATORS, VALIDATOR_NAMES, WEIGHTS
from bet import Bet
from view import View
from adversary import Adversary
from network import Network

network = Network()
network.random_initialization()

print "WEIGHTS", WEIGHTS

decided = dict.fromkeys(VALIDATOR_NAMES, 0)

while(True):
    network.report(decided)

    l = []

    for i in xrange(NUM_VALIDATORS):
        l.append(network.validators[i].my_latest_bet)

    for i in xrange(NUM_VALIDATORS):
        for j in xrange(NUM_VALIDATORS):
            if i != j and (r.randint(0, 4) == 0):
                network.propagate_bet_to_validator(l[j], i)

        if not decided[i]:
            network.get_bet_from_validator(i)
            for v in VALIDATOR_NAMES:
                decided[v] = network.validators[v].decided
            # print "decided:", decided

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
