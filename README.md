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
kernprof -l casper.py rounds && python -m line_profiler casper.py.lprof > results.txt
```
OR
```
kernprof -l casper.py blockchain && python -m line_profiler casper.py.lprof > results.txt
```
