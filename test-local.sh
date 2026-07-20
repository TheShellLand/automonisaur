#!/bin/bash

# run tests with env vars

cd $(dirname $0) && set -e

set -x
source env-local.sh && python3 -m pytest $@
