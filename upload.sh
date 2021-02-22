#!/bin/bash

# upload to pypi

cd $(dirname $0) && set -xe

if [ "$@" == '--local' ]; then
  source env.sh
  python3 setup.py sdist bdist_wheel
  twine check dist/*
  python3 -m twine upload --repository $PYPI --repository-url $TWINE_REPOSITORY \
    -u $TWINE_USERNAME -p $TWINE_PASSWORD --non-interactive --skip-existing dist/*
  python3 setup.py clean --all
else
  ./build.sh
  docker run --rm -it --env-file env.sh automon "$@"
fi
