#!/bin/bash
set -e
set -x
rm -rf \
    ~/.local/lib/python2.7/site-packages/concrete* \
    ~/Library/Python2.7/lib/python/site-packages/concrete* \
    build concrete.egg-info
python setup.py install --user
