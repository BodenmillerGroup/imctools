SHELL := /bin/bash

clean:
	find . -type d -name __pycache__ -exec rm -r {} \+
	find . -type d -name .pytest_cache -exec rm -r {} \+
	find . -type d -name .mypy_cache -exec rm -r {} \+
	find . -name '*.egg-info' -exec rm -fr {} +
	rm -fr build/
	rm -fr dist/
	rm -fr tests/testdata
	rm -fr docs/build

# Install all development dependencies
install:
	poetry install

# Build pip package
build:
	poetry build

# Publish pip package to PyPI
publish:
	poetry publish

update:
	poetry update && poetry install

pylint:
	pylint imctools

# Check style with flake8
flake8:
	flake8 imctools tests

test:
	pytest

# Check code test coverage
coverage:
	pytest --cov=imctools tests/

build-docs:
	rm -fr docs/build
	cd docs && make html

mypy:
	mypy imctools

pyright:
	pyright imctools

isort:
	isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 imctools

vulture:
	vulture imctools --min-confidence 70

black:
	black imctools

autoflake:
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place imctools --exclude=__init__.py
