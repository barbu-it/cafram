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
    python $i
    #python examples/$i
  done
}

run_tests ()
{
  #echo "=> Run test suite: pytest -x tests/test_nodes.py"
  #pytest -x tests/test_nodes.py

  pytest --cov=cafram tests -v $@
}

main ()
{

  run_tests
  run_examples

  echo "---"
  echo "Tests are over with Success!"
}


main $@




#  #!/bin/bash
#  #pytest --cov=cafram  --cov-branch --cov-report term-missing -vv tests
#  #pytest --cov=cafram  --cov-report term-missing -vv tests
#  pytest --cov=cafram  tests -v $@
#  
#  behave features/
#  
