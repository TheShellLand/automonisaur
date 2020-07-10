#!/bin/bash

set -ex

pytest --cov=automon --cov-report html automon
