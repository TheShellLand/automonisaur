#!/bin/bash

cd $(dirname $0) && set -e

# TODO: set pre-commit hook

if [ -f env.sh ]; then source env.sh; fi

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
  pytest --cov=automon --cov-report term "$@"
fi


if [ ! -z "$CODECOV_TOKEN" ] && [[ "$@" == "html" ]]; then
  bash <(curl -s https://codecov.io/bash)
fi
