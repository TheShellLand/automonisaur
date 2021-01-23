#!/bin/bash

# entrypoint

set -e
cd $(dirname $0)

if [ "$1" == "test" ]; then
  /bin/bash unittests.sh "$2"
else
  python3 -m twine upload --repository $PYPI --skip-existing dist/* || exec "$@"
fi

exec "$@"
