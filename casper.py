'''
Casper PoC: Correct-by-construction asynchronous binary consensus.

Note that comments marked with "#########....#########"" barriers are probably
conceptually important Other comments may be conceptually important but are
mostly for code comprehension Note that not all comments have been marked up in
this manner, yet... :)
'''

import sys

import casper.presets as presets
from casper.simulation_utils import (
    generate_random_validator_set
)
from simulations.simulation_runner import SimulationRunner


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

    simulation_runner = SimulationRunner(validator_set, msg_gen, 100, True)
    simulation_runner.run()


if __name__ == "__main__":
    main()
