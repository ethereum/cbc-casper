.PHONY: install test

install:
	( \
	   python3 -m venv venv; \
	   . venv/bin/activate; \
	   pip install -r requirements.txt; \
	)

test:
	venv/bin/pytest $(TEST)

test-with-reports:
	venv/bin/pytest $(TEST) --report

lint:
	venv/bin/pylint casper/

MODE?=rand

run-binary:
	venv/bin/python casper.py $(MODE) --protocol binary

run-blockchain:
	venv/bin/python casper.py $(MODE) --protocol blockchain

run-concurrent:
	venv/bin/python casper.py $(MODE) --protocol concurrent

run-integer:
	venv/bin/python casper.py $(MODE) --protocol integer

run-order:
	venv/bin/python casper.py $(MODE) --protocol order

run-sharding:
	venv/bin/python casper.py $(MODE) --protocol sharding
