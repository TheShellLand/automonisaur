#!/bin/bash

# get all the docker images used for local testing

set -xe

images="
minio
elasticsearch
kibana
filebeat
metricbeat
neo4j
nmap
"

for i in $images; do
  docker pull $i
  docker images | grep $i
done

echo done

