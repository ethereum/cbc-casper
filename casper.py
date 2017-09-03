'''
Casper PoC: Correct-by-construction asynchronous binary consensus.

Note that comments marked with "#########....#########"" barriers are probably
conceptually important Other comments may be conceptually important but are
mostly for code comprehension Note that not all comments have been marked up in
this manner, yet... :)
'''

import sys

import random as r  # to ensure the tie-breaking property
import settings as s

from justification import Justification
from view import View
from network import Network
from validator import Validator
import forkchoice
import plot_tool
import presets


def main():
    
    network = Network()

    print "WEIGHTS", s.WEIGHTS

    decided = dict.fromkeys(s.VALIDATOR_NAMES, 0)
    safe_messages = set()

    network.random_initialization()
    network.report()
    blockchain = []
    communications = []

    mode = sys.argv[1]
    if mode != "rand" and mode != "rrob" and mode != "full" and mode != "nofinal":
        print "\nusage: 'kernprof -l casper.py (rand | rrob | full | nofinal)'\n"
        return
    msg_gen = presets.message_maker(mode)

    iterator = 0
    while(True):
        iterator += 1

        messages = msg_gen()

        old_blocks = []
        for i in xrange(s.NUM_VALIDATORS):
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
        for j in xrange(s.NUM_VALIDATORS):
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

        if iterator % s.REPORT_INTERVAL == 0:

            best_block = network.global_view.estimate()
            best_chain = forkchoice.build_chain(best_block, None)

            vs_chain = []
            for i in xrange(s.NUM_VALIDATORS):
                vs_chain.append(forkchoice.build_chain(network.validators[i].my_latest_message(), None))

            print "BEST CHAIN----------------------", best_chain


            edgelist = []

            edgelist.append({'edges':blockchain, 'width':2,'edge_color':'grey','style':'solid'})
            edgelist.append({'edges':communications, 'width':1,'edge_color':'black','style':'dotted'})
            edgelist.append({'edges':best_chain, 'width':5,'edge_color':'red','style':'solid'})
            for i in xrange(s.NUM_VALIDATORS):
                edgelist.append({'edges':vs_chain[i],'width':2,'edge_color':'blue','style':'solid'})

            #coloured_blocks = network.global_view.latest_messages.values()
            network.report(edges=edgelist)

            #for i in xrange(s.NUM_VALIDATORS):
            #    plot_tool.plot_view(network.validators[i].view)

main()
