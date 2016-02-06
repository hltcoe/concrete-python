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

# stupid snake
cat /etc/profile.d/conda.sh
echo 'export PATH="/usr/local/bin:$PATH"' >> /etc/profile.d/conda.sh
