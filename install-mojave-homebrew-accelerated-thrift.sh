#!/bin/bash

# Install accelerated version of Python Thrift library on macOS Mojave
#
# This simple shell script makes a bunch of assumptions that it does
# not bother to check, including:
#   - You are on a Mac running macOS Mojave
#   - You have Xcode installed
#   - You have the Homebrew package manager (https://brew.sh) installed
#   - You have pip installed

brew install thrift

export CFLAGS="-stdlib=libc++ -I/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include/c++/v1"

pip install --force-reinstall --no-binary :all: --verbose thrift==0.11.0

scripts/thrift-is-accelerated.py
