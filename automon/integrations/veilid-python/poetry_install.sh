#!/bin/bash
poetry config --local virtualenvs.in-project true
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
poetry install
