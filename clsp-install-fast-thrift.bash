#!/bin/bash

set -e

tar -xzf /export/a13/cmay/thrift-py-1.0.0.dev0.tar.gz
cd thrift-py-1.0.0.dev0
python setup.py install --user
