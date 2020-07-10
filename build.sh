#!/bin/bash

# image build script

set -xe
cd $(dirname $0)

DOCKERNAME=automon-core

# build image
DOCKERTAG=$(git describe --tags)
docker build -t $DOCKERNAME:$DOCKERTAG .
docker tag $DOCKERNAME:$DOCKERTAG $DOCKERNAME:latest

# list image
docker images | grep $DOCKERNAME
