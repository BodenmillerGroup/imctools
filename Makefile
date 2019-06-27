SHELL := /bin/bash

init:
	poetry install

build:
	poetry build

publish:
	poetry publish

update:
	poetry update && poetry install

clean:
	find . -type d -name __pycache__ -exec rm -r {} \+
	find . -type d -name .pytest_cache -exec rm -r {} \+
	find . -type d -name .mypy_cache -exec rm -r {} \+
	find . -name '*.egg-info' -exec rm -fr {} +
	rm -fr build/
	rm -fr dist/
	rm -fr docs/build/

lint: ## check style with flake8
	flake8 imctools tests

test: ## run tests quickly with the default Python
	pytest

coverage: ## check code coverage
	pytest --cov=imctools tests/

generate-docs:
	sphinx-build -M html "docs/source" "docs/build" $(O)
