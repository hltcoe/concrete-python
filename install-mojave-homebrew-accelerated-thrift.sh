#!/bin/bash

# Install accelerated version of Python Thrift library on macOS Mojave
#
# This simple shell script makes a bunch of assumptions that it does
# not bother to check, including:
#   - You are on a Mac running macOS Mojave
#   - You have Xcode installed
#   - You have the Homebrew package manager (https://brew.sh) installed
#   - You have pip installed


# Install Thrift 0.11.0 using older Homebrew formula
#
# As of 2019-05-19, Homebrew installs Thrift 0.12.0 by default, but
# the most recent version of the thrift Python package is 0.11.0.
brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/a1d5a1e87bccf56b741a1276f0b305baadca0e16/Formula/thrift.rb

export CFLAGS="-stdlib=libc++ -I/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include/c++/v1"

pip install --force-reinstall --no-binary :all: --verbose thrift==0.11.0

scripts/thrift-is-accelerated.py
