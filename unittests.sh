#!/bin/bash

set -ex
cd $(dirname $0)

# TODO: set pre-commit hook

pytest --cov=automon --cov-report term automon
