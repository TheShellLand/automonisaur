#!/bin/bash

# clean repo

cd $(dirname $0) && set -xe

git clean -xdf $@ --exclude env.sh --exclude .idea

