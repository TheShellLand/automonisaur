#!/bin/bash

# image build script

cd $(dirname $0) && set -xe

/bin/bash build.sh && docker run --rm -it automon "$@"
