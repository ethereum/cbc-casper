'''
Casper PoC: Correct-by-construction asynchronous binary consensus.

Note that comments marked with "#########....#########"" barriers are probably
conceptually important Other comments may be conceptually important but are
mostly for code comprehension Note that not all comments have been marked up in
this manner, yet... :)
'''

import sys

import casper.settings as s
from casper.network import Network
from casper.safety_oracles.clique_oracle import CliqueOracle
import casper.utils as utils
import casper.presets as presets
from casper.simulation_utils import (
    generate_random_validator_set
)


def main():
    mode = sys.argv[1]
    if mode not in ["rand", "rrob", "full", "nofinal"]:
        print(
            "\nusage: 'kernprof -l casper.py (rand | rrob | full | nofinal)'\n"
        )
        return
    msg_gen = presets.message_maker(mode)

    validator_set = generate_random_validator_set()
    print("WEIGHTS: {0}".format(validator_set.validator_weights()))

    network = Network(validator_set)
    network.random_initialization()
    network.report()

    blockchain = []
    communications = []
    safe_blocks = set()
    node_ft = dict()

    iterator = 0
    while True:
        iterator += 1

        message_paths = msg_gen(validator_set)

        sending_validators = {i for i, j in message_paths}
        affected_validators = {j for i, j in message_paths}

        # Get the most recent messages from sending validators
        old_messages = {}
        for sender in sending_validators:
            # We assume here that validators all have a most recent message
            old_messages[sender] = sender.my_latest_message()

        # Send these messages to the respective recieving validators
        for sender, reciever in message_paths:
            network.propagate_message_to_validator(old_messages[sender], reciever)

        # Have recieving/affected validators make new blocks
        new_messages = {}
        for v in affected_validators:
            new_message = network.get_message_from_validator(v)
            new_messages[v] = new_message
            # Update display to show this new message properly
            if new_message.estimate is not None:
                blockchain.append([new_message, new_message.estimate])

            # Have validators try to find newly finalized blocks
            curr = new_message
            last_finalized_block = v.view.last_finalized_block
            while curr != last_finalized_block:
                if v.check_estimate_safety(curr):
                    break
                curr = curr.estimate

        # Add all new messages to the global_view
        # network.global_view.add_messages(new_messages.values())

        # Display the fact that these messages propagated
        for sender, reciever in message_paths:
            communications.append([old_messages[sender], new_messages[reciever]])

        # Display the fault tolerance in the global view
        tip = network.global_view.estimate()
        while tip and node_ft.get(tip, 0) != s.NUM_VALIDATORS - 1:
            # TODO: decide which oracle to use when displaying global ft.
            # When refactoring visualizations, could give options to switch
            # between different oracles while displaying a view!
            oracle = CliqueOracle(tip, network.global_view)
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                safe_blocks.add(tip)
                node_ft[tip] = num_node_ft

            tip = tip.estimate

        if iterator % s.REPORT_INTERVAL == 0:

            # Build the global forkchoice, so we can display it!
            best_block = network.global_view.estimate()
            best_chain = utils.build_chain(best_block, None)

            # Build each validators forkchoice, so we can display as well!
            vals_chain = []
            for v in validator_set:
                vals_chain.append(
                    utils.build_chain(v.my_latest_message(), None)
                )

            edgelist = []
            edgelist.append({'edges':blockchain, 'width':2,'edge_color':'grey','style':'solid'})
            edgelist.append({'edges':communications, 'width':1,'edge_color':'black','style':'dotted'})
            edgelist.append({'edges':best_chain, 'width':5,'edge_color':'red','style':'solid'})
            for vals in vals_chain:
                edgelist.append({'edges':vals,'width':2,'edge_color':'blue','style':'solid'})

            network.report(edges=edgelist, colored_messages=safe_blocks, color_mag=node_ft)


if __name__ == "__main__":
    main()
