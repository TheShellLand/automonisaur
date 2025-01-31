#!/bin/bash

# image build script

cd "$(dirname "$0")" && set -xe

source config.sh

# build image
docker buildx build "$@" \
  --platform linux/arm/v7,linux/arm64/v8,linux/amd64 \
  -f $DOCKERFILE \
  --tag $DOCKERNAME:$DOCKERTAG ..

docker tag $DOCKERNAME:$DOCKERTAG $DOCKERNAME:latest

# list image
docker images | grep $DOCKERNAME
