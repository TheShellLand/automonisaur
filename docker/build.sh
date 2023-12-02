#!/bin/bash

# image build script

cd "$(dirname "$0")" && set -xe

DOCKERNAME=automon
DOCKERTAG=$(git describe --tags)
DOCKERFILE=../Dockerfile

# build image
docker build "$@" -t $DOCKERNAME:$DOCKERTAG -f $DOCKERFILE ..
docker tag $DOCKERNAME:$DOCKERTAG $DOCKERNAME:latest

# list image
docker images | grep $DOCKERNAME
