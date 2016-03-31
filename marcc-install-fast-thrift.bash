#!/bin/bash

set -e

tar -xzf /scratch/groups/bvandur1/thrift-py-1.0.0.dev0.tar.gz
cd thrift-py-1.0.0.dev0
python setup.py install --user
