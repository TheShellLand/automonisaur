#!/bin/bash

# image build script

cd "$(dirname "$0")" && set -xe

source config.sh

if [ "${DOCKER_PRUNE}" == 1 ]; then
  docker image prune -f
fi

if [ "${DOCKER_DELETE}" == 1 ]; then
   docker image rm -f $(docker image ls | grep $DOCKERNAME | awk '{print $3}') || echo "DOCKER DELETE DONE"
fi


# build image
docker buildx build "$@" \
  --platform linux/arm64/v8,linux/amd64 \
  -f $DOCKERFILE \
  --tag $DOCKERNAME:$DOCKERTAG ..

docker tag $DOCKERNAME:$DOCKERTAG $DOCKERNAME:latest

# list image
docker images | grep $DOCKERNAME
