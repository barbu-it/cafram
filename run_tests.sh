#!/bin/bash

#pytest --cov=cafram  --cov-branch --cov-report term-missing -vv tests
#pytest --cov=cafram  --cov-report term-missing -vv tests
pytest --cov=cafram  -vv tests $@

