#!/bin/bash


if [ $# -ne 1 ]
then
    echo "Usage: $0 CONCRETE-THRIFT-PATH" >&2
    exit 1
fi

concrete_thrift_path="$1"


set -e


if [ -e b ]
then
    echo 'Backing up b...'
    mv b b.`date +%Y%m%d%H%M%S`
fi
echo 'Copying current concrete to b...'
cp -a concrete b
echo
echo

if [ -e a ]
then
    echo 'Backing up a...'
    mv a a.`date +%Y%m%d%H%M%S`
fi
echo 'Building raw classes in a...'
mkdir a
echo '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
bash build.bash --output-dir a --raw "$concrete_thrift_path"
echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
echo
echo

echo 'Generating patches from a to b...'
rm -rf patches
mkdir patches
for path in a/*
do
    if [ -d "$path" ]
    then
        bn=`basename "$path"`
        diff -ruN -x '*.pyc' a/$bn b/$bn > patches/${bn}.patch || true
    fi
done
echo
echo

echo 'Verifying build...'
echo '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
bash build.bash "$concrete_thrift_path"
echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
echo
echo

echo 'Done.'
echo
echo 'If build above succeeded and the output is as desired, then the'
echo 'patches have been generated successfully.  If not, something is'
echo 'wrong.  Note that your original concrete/ files are now in b/.'
