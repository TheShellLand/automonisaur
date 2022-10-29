#!/bin/bash

cd $(dirname $0); set -xe

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade -r requirements.txt

cat requirements.txt  | grep -v "^$" | grep -v "#" | sort -h | sed 's/$/"/' | sed 's/^/"/' | sed 's/$/,/' | sed "s/\"/'/g"

