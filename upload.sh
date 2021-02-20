#!/bin/bash

# upload to pypi

cd $(dirname $0) && set -xe

./build.sh

docker run --rm -it --env-file env.sh automon "$@"
