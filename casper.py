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
import plot_tool


def main():

    network = Network()

    print "WEIGHTS", WEIGHTS

    decided = dict.fromkeys(VALIDATOR_NAMES, 0)
    safe_messages = set()

    network.random_initialization()
    network.report()
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

        old_blocks = []
        for i in xrange(NUM_VALIDATORS):
            if network.validators[i].my_latest_message() is not None:
                old_blocks.append(network.validators[i].my_latest_message())

        sending_validators = set()
        affected_validators = set()
        successful_paths = []
        for path in messages:
            i = path[0]
            j = path[1]
            old_block = old_blocks[i]

            if old_block not in network.validators[j].view.messages:
                network.propagate_message_to_validator(old_block, j)
                sending_validators.add(i)
                affected_validators.add(j)
                successful_paths.append([i, j])

        new_blocks = []
        for j in xrange(NUM_VALIDATORS):
            if j in affected_validators:
                new_block = network.get_message_from_validator(j)
                new_blocks.append(new_block)

                successful_paths.append([j, j])

                if new_block.estimate is not None:
                    blockchain.append([new_block, new_block.estimate])

        for ij in successful_paths:
            for b in new_blocks:
                if b.sender == ij[1]:
                    communications.append([old_blocks[ij[0]], b])

        network.global_view.add_messages(new_blocks)

        if iterator % REPORT_INTERVAL == 0:

            best_block = network.global_view.estimate()
            best_chain = []
            next_block = best_block
            while next_block is not None:
                if next_block.estimate is not None:
                    best_chain.append((next_block, next_block.estimate))
                next_block = next_block.estimate

            print "BEST CHAIN----------------------", best_chain


            edgelist = []

            edgelist.append({'edges':blockchain, 'width':3,'edge_color':'grey','style':'dashed'})
            edgelist.append({'edges':communications, 'width':1,'edge_color':'black','style':''})
            edgelist.append({'edges':best_chain, 'width':10,'edge_color':'red','style':''})
            #coloured_blocks = network.global_view.latest_messages.values()
            network.report(edges=edgelist)

            #for i in xrange(NUM_VALIDATORS):
            #    plot_tool.plot_view(network.validators[i].view)

    else:
        print "\nusage: 'kernprof -l casper.py rounds' or 'kernprof -l casper.py blockchain'\n"

main()
