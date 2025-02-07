#!/bin/bash

# image build script

cd "$(dirname "$0")" && set -xe

source config.sh

DOCKERNAME=$DOCKERNAME
/bin/bash build.sh && docker run --rm $DOCKERNAME pytest "$@"
