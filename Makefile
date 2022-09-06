clean:
	rm -rf day-summary *.checkpoint .pytest_cache .coverage .venv/

init: clean
	pip install poetry 
	poetry install

test:
	poetry run python -m pytest

#CI/CD
ci-setup:
	pip install poetry
	poetry install 

ci-test:
	poetry run python -m pytest 
