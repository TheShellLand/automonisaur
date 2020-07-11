#!/bin/bash

set -e
cd $(dirname $0)

# TODO: set pre-commit hook

if [ -z "$@" ]; then
  pytest --cov=automon -v --cov-report term automon
elif [ "$@" == "html" ]; then
    pytest --cov=automon -v --cov-report html automon
else
  pytest --cov=automon -v --cov-report term "$@"
fi
