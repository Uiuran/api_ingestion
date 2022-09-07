clean:
	rm -rf day-summary *.checkpoint .pytest_cache .coverage .venv/

init: clean
	pip install -r requirements.txt
	pip install .

test:
	python -m pytest

#CI/CD
ci-setup:
	pip install -r requirements.txt
	pip install . 

ci-test:
	python -m pytest 

ci-deploy:
	zappa update $(stage) || zappa deploy $(stage)

ci-destroy:
	zappa undeploy $(stage)
