#!/bin/bash

set -e

echo 'Checking for Twisted trial support...'
if ! python -c 'import twisted.trial'
then
    echo 'the Thrift Python library requires Twisted,' >&2
    echo 'install it with:  pip install --user Twisted' >&2
    exit 1
fi

git clone https://github.com/cjmay/thrift.git cjmay-thrift
cd cjmay-thrift
./bootstrap.sh
PY_PREFIX=$HOME/.local CFLAGS=-D__STDC_LIMIT_MACROS ./configure \
    --prefix=$HOME \
    --with-python \
    --without-{c_glib,cpp,java,erlang,php}

echo 'does the configure output above indicate the Python library will'
echo -n 'be built? (answer y/n): '
read ans
if [ "$ans" != y -a "$ans" != yes ]
then
    echo 'build aborted by user, are Python headers not installed?' >&2
    exit 1
fi

make
make install
