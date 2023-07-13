#!/bin/bash
# Run QA tests
set -eu

./fix_qa.sh check

mypy -p cafram
pylint -f colorized cafram

echo "INFO: All QA tests passed (pylint+black)"
