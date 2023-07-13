#!/bin/bash
# Auto live run python tests
set -eu

# Require: https://github.com/rhpvorderman/pytest-notification
ptw . --notify -v || ptw . -v

# Custom runner
#ptw  --runner ./run_tests.sh  .

