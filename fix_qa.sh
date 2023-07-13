#!/bin/bash
# Lint and changes all files
set -eu


if [[ "${1:-}" == "check" ]] ; then
  FIX=false
elif [[ "${1:-}" == "fix" ]] ; then
  FIX=true
elif [[ "${1:-}" != "" ]] ; then
  echo "ERROR: Argument must can be: check|fix"
  exit 1
else
  echo "INFO: Script will autofix code"
  FIX=true
fi


lint_python()
{
  local regex=$1
  local files=$(git ls-files | grep '\.py$' | grep -E "$regex" | xargs )
  if [[ -n "$files" ]]; then
    if [[ "$FIX" == "true" ]] ; then
      black $files
      isort $files
    else
      black --check $files
      isort --check $files
    fi
  fi
}

lint_python cafram/
lint_python tests/
lint_python examples/

echo "INFO: Automatic linting is done (black + isort)"

