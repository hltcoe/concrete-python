#!/bin/bash

CONCRETE_PATH="../concrete_craig"

rm setup.py
rm -rf concrete

cp -a ${CONCRETE_PATH}/python/setup.py .
cp -a ${CONCRETE_PATH}/python/concrete/ concrete/
