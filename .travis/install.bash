#!/bin/bash

set -e
set -x

if [ `uname -s` == Darwin ]
then
    brew update
    brew install openssl zlib
    hash -r
    export LDFLAGS="-L/usr/local/opt/openssl/lib -L/usr/local/opt/zlib/lib"
    export CPPFLAGS="-I/usr/local/opt/openssl/include -I/usr/local/opt/zlib/include"
fi

if ! command -v python3.5
then
    pushd /tmp
    curl https://www.python.org/ftp/python/3.5.7/Python-3.5.7.tgz | tar -xz && \
        cd Python-3.5.7 && \
        ./configure --prefix=/usr/local && \
        make && \
        sudo make altinstall && \
        cd /tmp && \
        sudo rm -rf Python-3.5.7
    popd
fi

if ! command -v tox
then
    sudo pip3.5 install --upgrade 'tox>=4'
fi
