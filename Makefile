clean:
	rm -rf day-summary *.checkpoint .pytest_cache .coverage .venv/

init: clean
	pip install -r requirements.txt
	pip install .

test:
	python -m pytest

#CI/CD
ci-setup:
	python -m venv venv
	source .venv/bin/activate
	pip install -r requirements.txt
	pip install . 

ci-test:
	python -m pytest 

ci-deploy:
	zappa update $(stage) || zappa deploy $(stage)
