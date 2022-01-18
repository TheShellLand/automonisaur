$!/bin/bash

# test serverless function

set -xe

functions_framework --debug --target=$@

