#!/bin/bash

# upload to pypi

cd $(dirname $0) && set -e

if [ "$@" == '--local' ]; then
  set -x
  source env.sh
  python3 -m pip install -U twine
  python3 setup.py sdist bdist_wheel
  twine check dist/*
  python3 -m twine upload --repository $PYPI --repository-url $TWINE_REPOSITORY \
    -u $TWINE_USERNAME -p $TWINE_PASSWORD --non-interactive --skip-existing dist/*
  python3 setup.py clean --all
elif [ "$@" == '--docker' ]; then
  set -x
  /bin/bash docker/build.sh
  docker run --rm -it --env-file env.sh automon "$@"
elif [ "$@" == '--github' ]; then
  set -x
  python3 -m pip install -U twine
  python3 setup.py sdist bdist_wheel
  twine check dist/*
  python3 -m twine upload --repository $PYPI --repository-url $TWINE_REPOSITORY \
    -u $TWINE_USERNAME -p $TWINE_PASSWORD --non-interactive --skip-existing dist/*
fi
