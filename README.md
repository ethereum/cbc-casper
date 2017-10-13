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
