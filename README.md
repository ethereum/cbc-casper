Requires: matplotlib, networkx, imageio, line_profiler

This code is marked up for use as follows:
```
kernprof -l casper.py rounds && python -m line_profiler casper.py.lprof > results.txt
```
OR
```
kernprof -l casper.py blockchain && python -m line_profiler casper.py.lprof > results.txt
```
