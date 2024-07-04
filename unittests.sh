#!/bin/bash

# unittests

cd $(dirname $0) && set -e

rm -rf .coverage coverage.xml htmlcov

if [[ "$@" == "-v" ]]; then
  pytest --cov=automon -v --cov-report term automon
elif [[ "$@" == "-l" ]]; then
    pytest -v automon
elif [[ "$@" == "-ll" ]]; then
    pytest automon
elif [[ "$@" == "html" ]]; then
    pytest --cov=automon --cov-report html automon
else
  pytest --cov-report term "$@"
fi
