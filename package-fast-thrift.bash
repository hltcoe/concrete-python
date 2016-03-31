#!/bin/bash

set -e

echo 'Checking we are in a thrift git clone...'
head -n 1 README.md | grep -q '^Apache Thrift$'
[ -d .git ]

echo 'Checking for Twisted trial support...'
if ! python -c 'import twisted.trial'
then
    echo 'the Thrift Python library requires Twisted,' >&2
    echo 'install it with:  pip install --user Twisted' >&2
    exit 1
fi

echo 'Building...'
./bootstrap.sh
PY_PREFIX=$HOME/.local CFLAGS=-D__STDC_LIMIT_MACROS ./configure \
    --prefix=$HOME \
    --with-python \
    --without-{c_glib,cpp,java,erlang,php,haskell}
make

echo 'Checking build...'
[ -f lib/py/build/*/thrift/protocol/fastbinary.so ]

echo 'Packaging...'
target=thrift-py-1.0.0.dev0
rm -rf $target
cp -r lib/py $target
tar -czf ${target}.tar.gz $target

echo "Packaged ${target}.tar.gz"
