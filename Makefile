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
	venv/bin/python casper.py --protocol binary --msg-mode $(MODE)

run-blockchain:
	venv/bin/python casper.py --protocol blockchain --msg-mode $(MODE) --network random

run-concurrent:
	venv/bin/python casper.py --protocol concurrent --msg-mode $(MODE)

run-integer:
	venv/bin/python casper.py --protocol integer --msg-mode $(MODE)

run-order:
	venv/bin/python casper.py --protocol order --msg-mode $(MODE)

run-sharding:
	venv/bin/python casper.py --protocol sharding --msg-mode $(MODE)
