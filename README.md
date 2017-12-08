# Casper CBC
A python implementation of members of a class of "correct-by-construction" consensus protocols (description slowly becoming available [here](https://github.com/ethereum/research/tree/master/papers/cbc-consensus)). Currently, it includes Casper the Friendly Ghost (a blockchain consensus protocol) and Casper the Friendly Binary Consensus Protocol. Specifications for these protocols are [here](https://github.com/ethereum/research/tree/master/papers/CasperTFG), but the implementation and the spec may deviate from the spec, as they are still moving targets:  

### Warning -- Codebase subject to substantial changes
This pre v1.0 implementation is under active development and experimentation
and might experience _significant_ organizational and substantive changes.
If you use components of this codebase, _expect_ breaking changes to be
introduced.

That said, we will try to detail any breaking changes in subsequent releases.

Branch    | Tests
----------|------
master    | [![CircleCI](https://circleci.com/gh/ethereum/cbc-casper/tree/master.svg?style=svg&circle-token=071bd3b625fc240222d1add41dc796ec8bee077d)](https://circleci.com/gh/ethereum/cbc-casper/tree/master)
develop   | [![CircleCI](https://circleci.com/gh/ethereum/cbc-casper/tree/develop.svg?style=svg&circle-token=071bd3b625fc240222d1add41dc796ec8bee077d)](https://circleci.com/gh/ethereum/cbc-casper/tree/develop)

## Requirements
* Python 3
* ubuntu/debian: `sudo apt-get install python3-dev python3-venv python3-tk`
* OSX via Homebrew: `brew install python3`


## Developer Setup
If you would like to hack on cbc-casper or run the simulations yourself, setup your dev environment with:

```
make install
```

## Run Simulations
### Standard
Standard simulations are marked up for use as follows:


```
make run-[rand | rrob | full | nofinal | binary]
```

`rand:` each round, some randomly selected validators propagate their most recent message to other randomly selected validators, who then create new messages.

`rrob:` each round, the creator of the last round's block sends it to the next receiver, who then creates a block.

`full:` each round, all validators receive all other validators previous messages, and then all create messages.

`nofinal:` each round, two simultaneous round-robin message propagations occur at the same time. This results in validators never being able to finalize later blocks (they may finalize initial blocks, depending on weight distribution).

`binary:` unlike the above message propagation schemes, this changes the protocol to cbc-casper with binary data structures! Instead of a blockchain, this protocol just comes to consensus on a single bit.

By default, a gif and associated images of the simulation will be saved in `graphs/graph_num_0/`. These settings can be modified, along with the number of validators, the number of messages that propagate per round, and the report interval in the `config.ini`.

### Advanced
Advanced simulations can be run with a little command line wizardy.
- First ensure that you are using the virtual environment via: `. venv/bin/activate`
- Simulations can then be run via `casper.py`. The following are example usages:
```
# run a simulation with 100 validators and random message propagation
python casper.py rand --validators 100

# run a simulation without displaying the viewgraphs, but instead save them and create a GIF
python casper.py rand --hide-display --save

# run a simulation with 20 validators and 1000 rounds of round robin message propagation,
# reporting every 100 rounds
python casper.py rrob --validators 6 --rounds 300 --report-interval 100

# get help and all options for casper.py
python casper.py --help
```

## Write Simulations
Simulations can be created/managed by `SimulationRunner`. See `casper.py` for sample usage.

More sample simulations with data collection will be added soon.

## Run Experiments
An Experiment runs a type of simulation some number of times, collects some
specified data on on each simulation and on aggregate of the simulations and
outputs the results in `.json` and `.csv ` formats for further analysis and visualizations.
Experimental output is written to `out/{experiment_name-timestamp}/`

The parameters of an experiment are specified via a `.json` file and are run
using the python script, `run_experiment.py`. For example:

```
python run_experiment.py experiments/orphan_rate.json
```

The following are the fields that make up an experiment to be defined in a `.json` file:

`msg_mode` (string): Specifies the message generation/propagation scheme. The
available schemes are "rand", "rrob", "full", and "nofinal".

`protocol` (string): Specifies the protocol to test. Available protocols are
"blockchain", "integer", and "binary".

`network` (string): Specifies the network model test. Available networks are
"no-delay", "constant", "linear", and "gaussian".

`num_simulations` (number): Specifies the number of simulations to run. Each
simulation starts with a fresh setup -- messages, validators, etc.

`rounds_per_sim` (number): Specifies the number of rounds of the message
propagation scheme to run per simulation.

`report_interval` (number): Specifies at which intervals of the message
propagation to collect data. For example, if `rounds_per_sim` is 100 and `report_interval` is 20,
the experiment will collect data at round 20, 40, 60, 80, and 100.

`data` (list): Specifies which types of data to collect from the simulations as
strings. The available types of data are the methods of `Analyzer`. New types of data
can be added by simply adding a method to Analyzer and referencing the method
name in `data` of an experiment.

`validator_info` (object): Specifies the parameters for generating a validator
set for each simulation.

`validator_info.gen_type` (string): Specifies the type of validator generation
scheme. The available schemes are "gauss" and "weights".

`validator_info.num_validators` (number): [*only "gauss" `gen_type`*]
Specifies the number of validators per validator set.

`validator_info.mu` (number): [*only "gauss" `gen_type`*]
Specifies the mean of the gaussian distribution used to generate validator weights.

`validator_info.sigma` (number): [*only "gauss" `gen_type`*]
Specifies the standard deviation of the gaussian distribution used to generate validator weights.

`validator_info.min_weight` (number): [*only "gauss" `gen_type`*]
Specifies the absolute minimum validator weight can result from the "gauss"
`gen_type`

`validator_info.weights` (array): [*only "weights" `gen_type`*]
Specifies an explicit set of validator weights to be used in each simulation.
It is formatted as a json array with positive numbers as values.

## Run Tests
To run all tests:

```
make test
```

To run a specific test, use (or the equivalent for whatever test you wish to run)

```
make test TEST=tests/test_safety_oracle.py
```

To run tests with visualizations:
```
make test-with-reports
```
Note: each view graph must be closed for the tests to continue running.
