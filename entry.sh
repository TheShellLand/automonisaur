#!/bin/bash

# entrypoint

set -e
cd $(dirname $0)

if [ "$1" == "test" ]; then
  pip install -r requirements.txt
  /bin/bash unittests.sh "$2"
else
  python3 setup.py sdist bdist_wheel
  twine check dist/*
  python3 -m twine upload --repository $PYPI --skip-existing dist/* || exec "$@"
  exit 0
fi

exec "$@"
