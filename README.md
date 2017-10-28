# Casper CBC
A python implementation of Vlad Zamfir's Correct by Construction Casper.

### Warning -- Codebase subject to substantial changes
This pre v1.0 implementation is under active development and experimentation
and might experience _significant_ organizational and substantive changes.
If you use components of this codebase, _expect_ breaking changes to be
introduced.

That said, we will try to detail any breaking changes in subsequent releases.

Branch    | Tests
----------|------
master    | [![CircleCI](https://circleci.com/gh/karlfloersch/cbc-casper/tree/master.svg?style=svg&circle-token=071bd3b625fc240222d1add41dc796ec8bee077d)](https://circleci.com/gh/karlfloersch/cbc-casper/tree/master)
develop   | [![CircleCI](https://circleci.com/gh/karlfloersch/cbc-casper/tree/develop.svg?style=svg&circle-token=071bd3b625fc240222d1add41dc796ec8bee077d)](https://circleci.com/gh/karlfloersch/cbc-casper/tree/develop)

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
Standard similuations are marked up for use as follows:
```
make run-[rand | rrob | full | nofinal]
```

`rand:` each round, some randomly selected validators propagate their most recent message to other randomly selected validators, who then create new messages.

`rrob:` each round, the creator of the last round's block sends it to the next receiver, who then creates a block.

`full:` each round, all validators receive all other validators previous messages, and then all create messages.

`nofinal:` each round, two simultaneous round-robin message propagations occur at the same time. This results in validators never being able to finalize later blocks (they may finalize initial blocks, depending on weight distribution).

The number of validators, the number of messages that propagate per round, and the report interval can be edited in `casper/settings.py`.

### Advanced
Advanced simulations can be run with a little command line wizardy.
- First ensure that you are using the virtual environment via: `. venv/bin/activate`
- Simulations can then be run via `casper.py`. The following are example usages:
```
# run a simulation with 100 validators and random message propogation
python casper.py rand --validators 100

# run a simulation with 20 validators and 1000 rounds of round robin message propogation,
# reporting every 100 rounds
python casper.py rrob --validators 6 --rounds 300 --report-interval 100

# get help and all options for casper.py
python casper.py --help
```

## Write Simulations
Simulations can be created/managed by `SimulationRunner`. See `casper.py` for sample usage.

More sample simulations with data collection will be added soon.

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
