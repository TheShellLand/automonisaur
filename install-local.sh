#!/bin/bash

# install library

cd "$(dirname $0)"; set -xe

python3 -m pip uninstall automonisaur -y
python3 -m pip install -e ./
