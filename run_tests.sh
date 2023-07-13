#!/bin/bash

set -eu

run_examples ()
{
  #local files="app1.py app_logger.py"
  #local files="app1.py app_inherit.py app_logger.py example1.py"

  # example1.py: Old version, must be updated
  local files="app_apiv2.py app_ident.py app_inherit.py app_logger.py app1.py"
  files=$(ls -1  examples/*.py )

  for i in $files; do
    if [[ "$i" == examples/_* ]]; then
      continue
    fi

    echo "=> Run test: python $i"
    python $i &>/dev/null
  done
}

run_tests ()
{
  # Run tests
  pytest --cov=cafram  --cov-branch --cov-report term-missing tests
}

main ()
{

  # Run code tests
  run_tests
  run_examples

  # Run Qulity tests
  ./run_qa.sh

  echo "INFO: Tests are over with Success!"
}

main $@

#  #!/bin/bash
#  #pytest --cov=cafram  --cov-branch --cov-report term-missing -vv tests
#  #pytest --cov=cafram  --cov-report term-missing -vv tests
#  pytest --cov=cafram  tests -v $@
#  
#  behave features/
#  
