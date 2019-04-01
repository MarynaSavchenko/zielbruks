[![Build Status](https://travis-ci.com/wgslr/zielbruks.svg?branch=develop)](https://travis-ci.com/wgslr/zielbruks)

# Installation

Guide to installing project's dependencies.

## (optional) Set up python virtual env

In order not to clutter the global python installation with packages required
by this project, it is useful to set up a virtual environment:
1. go to a directory **outside** of the repository
2. `python3 -m venv ./zielbruks-env` (or pick any other name for the environemnt)  
  this command will create a directory `zielbruks-env` where all the packages will be installed
3. each time you open a console to work on this pproject, run `source ./zielbruks-env/bin/activate` (assuming you're using bash or zsh and the paths are correct)


## Install dependencies

This repository contains `requirements.txt` file listing pip packages required to run the project. Install them:
- In a virtual env
  1. activate the virtual env
  2. `pip install -r requirements.txt`
- Globally
  1. `pip install --user -r requirements.txt`


# Tests and static analysis

## Running tests
`./manage.py test`

## Linter

Linter used is `pylint`.  
To run it, specify module(s) to check, e.g. `pylint scheduler zielbruks`.

Pylint is configured in `pylintrc` which can be used to adjust enforced rules.

## Type analysis

Python allows specyfing argument and returns types (see [PEP 484](https://www.python.org/dev/peps/pep-0484/)).
This project uses [mypy](https://github.com/python/mypy) to check type correctness.  
Invocation: `mypy scheduler zielbruks`