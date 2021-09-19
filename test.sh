#!/bin/bash

# image build script

cd $(dirname $0) && set -e

if [ "$@" == "" ]; then
  set -x
  python3 -m pytest automon
else
  set -x
  python3 -m pytest $@
fi
