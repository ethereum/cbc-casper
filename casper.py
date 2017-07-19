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

        blockchain = []
        communications = []
        iterator = 0
        while(True):
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
                if old_block in network.validators[j].view.messages:
                    continue
                network.propagate_message_to_validator(old_block, j)
                new_block = network.get_message_from_validator(j)
                communications.append([old_block, new_block])

                if new_block.estimate is not None:
                    blockchain.append([new_block, new_block.estimate])


            if iterator % REPORT_INTERVAL == 0:

                best_block = network.global_view.estimate()
                best_chain = []
                next_block = best_block
                while next_block is not None:
                    if next_block.estimate is not None:
                        best_chain.append((next_block, next_block.estimate))
                    next_block = next_block.estimate

                print "BEST CHAIN----------------------", best_chain

                coloured_blocks = network.global_view.latest_messages.values()

                network.report(colored_messages=coloured_blocks, edges=communications, thick_edges=blockchain, colored_edges=best_chain)

    else:
        print "\nusage: 'kernprof -l casper.py rounds' or 'kernprof -l casper.py blockchain'\n"

main()
