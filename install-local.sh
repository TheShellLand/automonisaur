#!/bin/bash

# install library

cd "$(dirname $0)"; set -xe

python3 -m pip uninstall automonisaur -y
python3 -m pip install --use-pep517 -e ./

set +x

if [ ! -z "$@" ]; then
  set -x
  python3 -m pip install -U "$@"
fi
