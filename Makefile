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
	venv/bin/python casper.py rand

run-rrob:
	venv/bin/python casper.py rrob

run-full:
	venv/bin/python casper.py full

run-nofinal:
	venv/bin/python casper.py nofinal

