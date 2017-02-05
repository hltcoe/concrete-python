#!/bin/bash

set -e
set -x

if [ `uname -s` == Darwin ]
then
    brew update
    brew install openssl
    brew link --force openssl
    hash -r
    export LDFLAGS=-L/usr/local/opt/openssl/lib
    export CPPFLAGS=-I/usr/local/opt/openssl/include
fi

if ! command -v python2.7
then
    pushd /tmp
    curl https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz | tar -xz && \
        cd Python-2.7.13 && \
        ./configure --prefix=/usr/local && \
        make && \
        sudo make altinstall && \
        cd /tmp && \
        sudo rm -rf Python-2.7.13
    popd
fi

if ! command -v python3.5
then
    pushd /tmp
    curl https://www.python.org/ftp/python/3.5.3/Python-3.5.3.tgz | tar -xz && \
        cd Python-3.5.3 && \
        ./configure --prefix=/usr/local && \
        make && \
        sudo make altinstall && \
        cd /tmp && \
        sudo rm -rf Python-3.5.3
    popd
fi

if ! command -v pip
then
    curl https://bootstrap.pypa.io/get-pip.py | python
fi

if ! command -v tox
then
    pip install --user --upgrade tox
fi
