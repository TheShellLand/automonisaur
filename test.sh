#!/bin/bash

# run tests

cd $(dirname $0) && set -e

if [ ! -z "$@" ]; then
  set -x
  python3 -m pytest --log-cli-level=DEBUG automon
else
  set -x
  python3 -m pytest --log-cli-level=DEBUG $@
fi
