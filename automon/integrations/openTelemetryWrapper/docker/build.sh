#!/bin/bash 

# build image 

cd "$(dirname $0)" && set -xe

docker build $@ -f Dockerfile -t opentelemetry-python .
