#!/bin/bash

set -e

echo 'Copying current concrete to b...'
cp -a concrete b

echo 'Building raw classes in a...'
bash build.bash --output a --raw ../concrete/thrift

echo 'Generating patches from a to b...'
rm -rf patches
mkdir patches
for path in a/*
do
    if [ -d "$path" ]
    then
        bn=`basename "$path"`
        diff -ruN -x '*.pyc' a/$bn b/$bn > patches/${bn}.patch
    fi
done

echo 'Verifying build...'
bash build.bash ../concrete/thrift

echo 'Done.'
echo
echo 'If build above succeeded and the output is as desired, then the'
echo 'patches have been generated successfully.  If not, something is'
echo 'wrong.  Note that your original concrete/ files are now in b/.'
