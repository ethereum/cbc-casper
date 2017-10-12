# Casper CBC
A python implementation of Vlad Zamfir's Correct by Construction Casper.
* Python 2.7 Support
* Python 3.X on roadmap


## Developer Setup
If you would like to hack on cbc-casper or run the simulations yourself, setup your dev environment with:
```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Run Simulations
This code is marked up for use as follows:
```
kernprof -l casper.py (rand | rrob | full | nofinal)
```

## Run Tests
To run all tests:
```
pytest
```
To run a specific test, use (or the equivalent for whatever test you wish to run)
```
pytest tests/test_safety_oracle.py
```

A `--report` flag can optionally be added to display test visualizations. Note: each view graph must be closed for the tests to continue running.
