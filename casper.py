'''
Casper PoC: Correct-by-construction asynchronous binary consensus.

Note that comments marked with "#########....#########"" barriers are probably
conceptually important Other comments may be conceptually important but are
mostly for code comprehension Note that not all comments have been marked up in
this manner, yet... :)
'''

import sys

import random as r  # to ensure the tie-breaking property
import casper.settings as s

from casper.justification import Justification
from casper.view import View
from casper.network import Network
from casper.validator import Validator
from casper.safety_oracles.clique_oracle import CliqueOracle
import casper.utils as utils
import casper.plot_tool as plot_tool
import casper.presets as presets


def main():

    network = Network()

    print "WEIGHTS", s.WEIGHTS

    mode = sys.argv[1]
    if mode != "rand" and mode != "rrob" and mode != "full" and mode != "nofinal":
        print "\nusage: 'kernprof -l casper.py (rand | rrob | full | nofinal)'\n"
        return
    msg_gen = presets.message_maker(mode)

    network.random_initialization()
    network.report()

    blockchain = []
    communications = []
    safe_blocks = set()
    node_ft = dict()


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
        for i, j in messages:
            old_block = old_blocks[i]

            if old_block not in network.validators[j].view.messages:
                network.propagate_message_to_validator(old_block, j)
                sending_validators.add(i)
                affected_validators.add(j)
                successful_paths.append([i, j])

        new_blocks = []
        for j in affected_validators:
            new_block = network.get_message_from_validator(j)
            new_blocks.append(new_block)

            successful_paths.append([j, j])

            curr = new_block
            last_finalized_block = network.validators[j].view.last_finalized_block
            while curr != last_finalized_block:
                if network.validators[i].check_estimate_safety(curr):
                    break
                curr = curr.estimate

            if new_block.estimate is not None:
                blockchain.append([new_block, new_block.estimate])

        for i, j in successful_paths:
            for b in new_blocks:
                if b.sender == j:
                    communications.append([old_blocks[i], b])

        network.global_view.add_messages(new_blocks)

        tip = network.global_view.estimate()
        while tip:
            if node_ft.get(tip, 0) == s.NUM_VALIDATORS - 1:
                break

            oracle = CliqueOracle(tip, network.global_view)
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                safe_blocks.add(tip)
                node_ft[tip] = num_node_ft

            tip = tip.estimate

        if iterator % s.REPORT_INTERVAL == 0:

            best_block = network.global_view.estimate()
            best_chain = utils.build_chain(best_block, None)

            vs_chain = []
            for i in xrange(s.NUM_VALIDATORS):
                vs_chain.append(utils.build_chain(network.validators[i].my_latest_message(), None))

            print "BEST CHAIN----------------------", best_chain


            edgelist = []

            edgelist.append({'edges':blockchain, 'width':2,'edge_color':'grey','style':'solid'})
            edgelist.append({'edges':communications, 'width':1,'edge_color':'black','style':'dotted'})
            edgelist.append({'edges':best_chain, 'width':5,'edge_color':'red','style':'solid'})
            for i in xrange(s.NUM_VALIDATORS):
                edgelist.append({'edges':vs_chain[i],'width':2,'edge_color':'blue','style':'solid'})

            #coloured_blocks = network.global_view.latest_messages.values()
            network.report(edges=edgelist, colored_messages=safe_blocks, color_mag=node_ft)

            #for i in xrange(s.NUM_VALIDATORS):
            #    plot_tool.plot_view(network.validators[i].view)


if __name__ == "__main__":
    main()
