#!/bin/bash

# image build script

cd $(dirname $0) && set -xe

python3 -m pytest automon
