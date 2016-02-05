#!/bin/bash

set -e
set -x

yum install -y \
    python \
    python-devel

curl https://bootstrap.pypa.io/get-pip.py | python
pip install --upgrade \
    flake8 \
    pytest \
    pytest-cov \
    setuptools \
    tox
