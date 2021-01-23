#!/bin/bash

# upload to pypi

cd $(dirname $0) && set -xe

docker run --rm -it --env-file env.sh automon
