#!/bin/bash

# entrypoint

set -e
cd $(dirname $0)

if [ "$1" == "test" ]; then
  /bin/bash unittests.sh "$2"
elif [ "$1" == "bash" ]; then
  exec "$@"
else
  python3 setup.py
fi
