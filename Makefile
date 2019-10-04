all: help

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  init                        to install python dependencies through pipenv"
	@echo "  sync                        update dependencies of pipenv"
	@echo "  lint                        to lint backend code (flake8)"

init:
	pipenv install --dev --ignore-pipfile

sync:
	pipenv sync --dev

lint:
	flake8 . --max-line-length=120 --ignore=N802