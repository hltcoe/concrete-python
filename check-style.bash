#!/bin/bash
set -e
flake8 concrete/util concrete/*.py \
     scripts examples \
     tests integration-tests
bash check-todo-fixme-hack.bash
