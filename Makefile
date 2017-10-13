.PHONY: install test

install:
	( \
	   python3 -m venv venv; \
	   . venv/bin/activate; \
	   pip install -r requirements.txt; \
	)

test:
	pytest

lint:
	pylint casper/

run-rand:
	kernprof -l casper.py rand

run-rrob:
	kernprof -l casper.py rrob

run-full:
	kernprof -l casper.py full

run-nofinal:
	kernprof -l casper.py nofinal

