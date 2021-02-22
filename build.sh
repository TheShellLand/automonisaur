#!/bin/bash

# image build script

cd $(dirname $0) && set -xe

DOCKERNAME=automon

# build image
DOCKERTAG=$(git describe --tags)
docker build "$@" -t $DOCKERNAME:$DOCKERTAG .
docker tag $DOCKERNAME:$DOCKERTAG $DOCKERNAME:latest

# list image
docker images | grep $DOCKERNAME
