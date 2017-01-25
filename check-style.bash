#!/bin/bash
set -e
flake8 --max-line-length=99 \
     concrete/util concrete/*.py \
     scripts/* examples/* \
     tests integration-tests
bash check-todo-fixme-hack.bash
