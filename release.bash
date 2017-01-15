#!/bin/bash

set -e

if [ $# -ne 1 -o "$1" == "-h" -o "$1" == "--help" ]
then
    echo "Usage: $0 <version>" >&2
    echo "* Increase master version to <version>, release;" >&2
    echo "* increase version to next beta;" >&2
    echo >&2
    echo "Example: $0 4.13.4" >&2
    echo "* Increase master version to 4.13.4, release;" >&2
    echo "* increase version to 4.13.5b0;" >&2
    exit 1
fi

master_release_version="$1"
major_minor=`echo "$master_release_version" | cut -d . -f 1-2`
master_release_patch=`echo "$master_release_version" | cut -d . -f 3`
master_next_version="$major_minor.$(($master_release_patch + 1))b0"

inc_version() {
    sed -i "s/^__version__ = '\(.*\)'$/__version__ = '$1'/" concrete/version.py
    if [ `git diff | wc -l` -gt 0 ]
    then
        git commit -am "Increase version to $1"
        return 0
    else
        return 1
    fi
}

confirm() {
    local ans
    read -n 1 ans
    if [ "$ans" != y -a "$ans" != Y ]
    then
        echo >&2
        echo 'Aborted by user.' >&2
        exit 3
    fi
    echo
}

echo
echo "Tip of master log:"
git log master | head
echo ---
echo
echo -n "Proceed (y/n)? "
confirm

echo
git checkout master

echo
echo -n "Current version in concrete/version.py on master: "
master_current_version=`sed "s/^__version__ = '\(.*\)'$/\1/;q" concrete/version.py`
echo $master_current_version
if [ "$master_release_version" != `echo "$master_current_version" | cut -d b -f 1` ]
then
    echo 'Error: current version should be beta of master version to be released.' >&2
    exit 2
fi
echo
echo "Computed master versions: $master_release_version, $master_next_version."
echo -n "Okay (y/n)? "
confirm

echo
git status
echo -n "Resetting working tree and index and cleaning.  Okay (y/n)? "
confirm
git reset --hard
git clean -f -d -x
echo "Releasing master version $master_release_version then updating version to"
echo -n "$master_next_version .  Okay (y/n)? "
confirm
inc_version "$master_release_version"
python setup.py sdist
twine upload dist/*
git tag -am v$master_release_version v$master_release_version
inc_version "$master_next_version"
git push gitlab master v$master_release_version
