#!/bin/bash

set -eu

git ls-files cafram/ | xargs  isort
git ls-files tests/ | xargs  isort

black cafram/
black tests/

echo "INFO: Automatic linting is done"
