#!/bin/bash

# unittests

cd $(dirname $0) && set -e

rm -rf .coverage coverage.xml htmlcov

if [[ "$@" == "-v" ]]; then
  pytest --log-cli-level=DEBUG --cov=automon -v --cov-report term automon
elif [[ "$@" == "-l" ]]; then
    pytest --log-cli-level=DEBUG -v automon
elif [[ "$@" == "-ll" ]]; then
    pytest --log-cli-level=DEBUG automon
elif [[ "$@" == "html" ]]; then
    pytest --log-cli-level=DEBUG --cov=automon --cov-report html automon
else
  pytest --log-cli-level=DEBUG --cov-report term "$@"
fi
