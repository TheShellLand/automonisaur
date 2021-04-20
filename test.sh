#!/bin/bash

# image build script

cd $(dirname $0) && set -xe

if [ "$1" == "--local" ]; then
  python3 -m pytest automon
else
  DOCKERNAME=automon
  ./build.sh
  docker run --rm $DOCKERNAME test "$@"
fi
