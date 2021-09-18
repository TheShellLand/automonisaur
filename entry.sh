#!/bin/bash

# entrypoint

cd $(dirname $0) && set -ex

if [ "$1" == "test" ]; then
  exec /bin/bash unittests.sh "$2"

elif [ "$1" == "upload" ]; then
  python3 setup.py sdist bdist_wheel
  twine check dist/*
  python3 -m twine upload --repository $PYPI --skip-existing dist/* || exec "$@"
  exit 0
fi

exec "$@"