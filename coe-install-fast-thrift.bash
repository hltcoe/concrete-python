#!/bin/bash

set -e

tar -xzf /export/projects/cmay/thrift-py-1.0.0.dev0.tar.gz
cd thrift-py-1.0.0.dev0
python setup.py install --user
