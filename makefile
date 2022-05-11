SHELL := /bin/bash

install:
	python3.9 -m venv venv; \
	source venv/bin/activate; \
	pip3 install --upgrade pip; \
	# pip3 install fnpb-alexjrlewis; \
	deactivate;

clean:
	@echo "Deleting virtual environment and python cache ..."; \
	rm -rf venv; \
	find . -type d -name __pycache__ -exec rm -r {} \+;

build:
	python3.10 -m pip install twine; \
	python3.10 -m twine upload --repository testpypi dist/*;
