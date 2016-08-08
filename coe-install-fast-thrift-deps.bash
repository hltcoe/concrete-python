#!/bin/bash

# usage:
#   bash coe-install-fast-thrift-deps.bash [configure-arg ...]
#
# for example, to install to your home directory, do:
#   bash coe-install-fast-thrift-deps.bash --prefix=$HOME

set -e
set -x

cd

wget http://ftp.gnome.org/pub/gnome/sources/glib/2.46/glib-2.46.2.tar.xz
wget http://pkgconfig.freedesktop.org/releases/pkg-config-0.29.tar.gz
wget http://ftp.gnu.org/gnu/autoconf/autoconf-2.69.tar.gz
wget http://ftp.gnu.org/gnu/automake/automake-1.15.tar.gz
wget ftp://sourceware.org/pub/libffi/libffi-3.2.1.tar.gz
wget http://ftp.gnu.org/gnu/bison/bison-2.7.1.tar.gz

shasums_temp=`mktemp`
cat > "$shasums_temp" << EOF
5031722e37036719c1a09163cc6cf7c326e4c4f1f1e074b433c156862bd733db  glib-2.46.2.tar.xz
c8507705d2a10c67f385d66ca2aae31e81770cc0734b4191eb8c489e864a006b  pkg-config-0.29.tar.gz
954bd69b391edc12d6a4a51a2dd1476543da5c6bbf05a95b59dc0dd6fd4c2969  autoconf-2.69.tar.gz
7946e945a96e28152ba5a6beb0625ca715c6e32ac55f2e353ef54def0c8ed924  automake-1.15.tar.gz
d06ebb8e1d9a22d19e38d63fdb83954253f39bedc5d46232a05645685722ca37  libffi-3.2.1.tar.gz
08e2296b024bab8ea36f3bb3b91d071165b22afda39a17ffc8ff53ade2883431  bison-2.7.1.tar.gz
EOF
sha256sum -c "$shasums_temp"
rm -f "$shasums_temp"

tar -xf glib-2.46.2.tar.xz
pushd glib-2.46.2
./configure "$@"
make
make install
popd
rm -rf glib-2.46.2 glib-2.46.2.tar.xz

tar -xf pkg-config-0.29.tar.gz
pushd pkg-config-0.29
./configure "$@"
make
make install
popd
rm -rf pkg-config-0.29 pkg-config-0.29.tar.gz

tar -xf autoconf-2.69.tar.gz
pushd autoconf-2.69
./configure "$@"
make
make install
popd
rm -rf autoconf-2.69 autoconf-2.69.tar.gz

tar -xf automake-1.15.tar.gz
pushd automake-1.15
./configure "$@"
make
make install
popd
rm -rf automake-1.15 automake-1.15.tar.gz

tar -xf libffi-3.2.1.tar.gz
pushd libffi-3.2.1
./configure "$@"
make
make install
popd
rm -rf libffi-3.2.1 libffi-3.2.1.tar.gz

tar -xf bison-2.7.1.tar.gz
pushd bison-2.7.1
./configure "$@"
make
make install
popd
rm -rf bison-2.7.1 bison-2.7.1.tar.gz
