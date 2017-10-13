# Casper CBC
A python implementation of Vlad Zamfir's Correct by Construction Casper.

## Requirements
* Python 3
* ubuntu/debian: `sudo apt-get install python3-venv`
* OSX via Homebrew: `brew install python3`


## Developer Setup
If you would like to hack on cbc-casper or run the simulations yourself, setup your dev environment with:

```
make install
```

## Run Simulations
This code is marked up for use as follows:
```
make run-[rand | rrob | full | nofinal]
```

`rand:` each round, some randomly selected validators propagate their most recent message to other randomly selected validators, who then create new messages.

`rrob:` each round, the creator of the last round's block sends it to the next receiver, who then creates a block.

`full:` each round, all validators receive all other validators previous messages, and then all create messages.

`nofinal:` each round, two simultaneous round-robin message propagations occur at the same time. This results in validators never being able to finalize later blocks (they may finalize initial blocks, depending on weight distribution).

The number of validators, the number of messages that propagate per round, and the report interval can be edited in `casper/settings.py`.


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
