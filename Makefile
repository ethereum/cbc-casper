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

run-rand:
	venv/bin/kernprof -l casper.py rand

run-rrob:
	venv/bin/kernprof -l casper.py rrob

run-full:
	venv/bin/kernprof -l casper.py full

run-nofinal:
	venv/bin/kernprof -l casper.py nofinal

