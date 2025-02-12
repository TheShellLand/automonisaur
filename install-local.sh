#!/bin/bash

# install library

cd "$(dirname $0)"; set -xe

python3 -m pip uninstall automonisaur -y
python3 -m pip install ./

set +x

if [ ! -z "$@" ]; then
  set -x
  python3 -m pip install -U "$@" && \
  rm -rf build/ dist/ automonisaur.egg-info/
fi
