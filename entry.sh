#!/bin/bash

# entrypoint

set -xe
cd $(dirname $0)

if [ "$1" == "test" ]; then
  /bin/bash unittests.sh
elif [ "$1" == "bash" ]; then
  exec "$@"
else
  python3 setup.py
fi
