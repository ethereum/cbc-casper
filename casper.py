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
from justification import Justification
from view import View
from network import Network

from validator import Validator


def main():

    if sys.argv[1] == 'test':

        network = Network()
        network.random_initialization()
        print network.global_view

    elif sys.argv[1] == 'rounds':

        network = Network()

        print "WEIGHTS", WEIGHTS

        decided = dict.fromkeys(VALIDATOR_NAMES, 0)
        safe_messages = set()

        network.random_initialization()

        edges = []
        iterator = 0
        while(iterator < 10):
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

            for path in messages:
                i = path[0]
                j = path[1]
                old_block = network.validators[i].my_latest_message()
                network.propagate_message_to_validator(old_block, j)
                new_block = network.get_message_from_validator(j)
                edges.append([old_block, new_block])

        print "len(edges)", len(edges)
        print "len(network.global_view.messages)", len(network.global_view.messages)
        network.report(safe_messages=set(), edges=edges)
        '''
        last_messages = []
        validator_received_messages = set()
        for i in xrange(NUM_VALIDATORS):
            last_messages.append(network.validators[i].my_latest_message())

        for sb in list(safe_messages):
            if sb not in last_messages:
                raise Exception("safe estimates should be in last messages")  # sanity check

        for path in messages:
            i = path[0]
            j = path[1]
            network.propagate_message_to_validator(last_messages[i], j)
            validator_received_messages.add(j)

        for i in xrange(NUM_VALIDATORS):
            if not decided[i] and i in validator_received_messages:
                new_message = network.get_message_from_validator(i)
                decided[i] = network.validators[i].check_estimate_safety(new_message.estimate)

                if decided[i]:d
                    safe_messages.add(new_message)

        for path in messages:
            edges.append([last_messages[path[0]], network.validators[path[1]].my_latest_message()])
            edges.append([last_messages[path[1]], network.validators[path[1]].my_latest_message()])

        '''
    else:
        print "\nusage: 'kernprof -l casper.py rounds' or 'kernprof -l casper.py blockchain'\n"

main()
