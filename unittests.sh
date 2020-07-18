#!/bin/bash

source env.sh

set -e
cd $(dirname $0)

# TODO: set pre-commit hook

if [ -z "$@" ]; then
  pytest --cov=automon -v --cov-report term automon
elif [ "$@" == "-l" ]; then
    pytest -v automon
elif [ "$@" == "-ll" ]; then
    pytest automon
elif [ "$@" == "html" ]; then
    pytest --cov=automon --cov-report html automon
else
  pytest --cov=automon -v --cov-report term "$@"
fi


if [ ! -z "$CODECOV_TOKEN" ]; then
  bash <(curl -s https://codecov.io/bash)
fi
