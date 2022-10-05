#!/bin/bash

# install library

set -xe

python3 -m pip uninstall automonisaur -y
python3 -m pip install --upgrade git+https://github.com/TheShellLand/automonisaur.git#egg
