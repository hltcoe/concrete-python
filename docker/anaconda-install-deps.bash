#!/bin/bash

set -e
set -x

pip install --upgrade \
    flake8 \
    pep8 \
    pip \
    pytest \
    pytest-cov \
    tox
