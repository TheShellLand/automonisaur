#!/bin/bash

# image build script

set -xe
cd $(dirname $0)

DOCKERNAME=automon-core

./build.sh

docker run --rm $DOCKERNAME test "$@"
