#!/bin/bash

cd $(dirname $0); set -xe

python3 -m pip install --break-system-packages --upgrade pip
python3 -m pip install --break-system-packages --upgrade -r requirements.txt

cat requirements.txt  | grep -v "^$" | grep -v "#" | sort -h | sed 's/$/"/' | sed 's/^/"/' | sed 's/$/,/' | sed "s/\"/'/g"
