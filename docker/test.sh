#!/bin/bash

# image build script

cd "$(dirname "$0")" && set -xe

DOCKERNAME=automon
/bin/bash build.sh && docker run --rm $DOCKERNAME test "$@"
